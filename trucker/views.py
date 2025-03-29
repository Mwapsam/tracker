from rest_framework import viewsets, views
from rest_framework.throttling import UserRateThrottle
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from spotter.settings.serializers import CustomTokenObtainPairSerializer
from trucker.exceptions import TripValidationError
from trucker.permissions import IsDriverOwner
from trucker.services.stop_services import calculate_fuel_stops
from .models import DutyStatus, LogEntry, Driver, Trip, Vehicle, Carrier, Stop
from .serializers import (
    DutyStatusSerializer,
    LogEntryCreateSerializer,
    LogEntrySerializer,
    DriverSerializer,
    TripSerializer,
    UserSerializer,
    VehicleSerializer,
    CarrierSerializer,
)
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from django.conf import settings
import logging
logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogEntryViewSet(viewsets.ModelViewSet):
    serializer_class = LogEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LogEntry.objects.all().order_by("-date")

    def create(self, request, *args, **kwargs):
        serializer = LogEntryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer


class CarrierViewSet(viewsets.ModelViewSet):
    queryset = Carrier.objects.all()
    serializer_class = CarrierSerializer


class CurrentUserAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = UserSerializer(user).data
        return Response(data, status=200)


class DutyStatusViewSet(viewsets.ModelViewSet):
    queryset = DutyStatus.objects.all()
    serializer_class = DutyStatusSerializer
    permission_classes = [IsAuthenticated]


class LatestStationsViewSet(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, driver_id):
        log_entry = (
            LogEntry.objects.filter(driver__id=driver_id).order_by("-date").first()
        )

        if not log_entry:
            return Response({"error": "No log entry found for this driver"}, status=404)

        substations = log_entry.duty_statuses.all().order_by("-start_time")[:3]

        data = DutyStatusSerializer(substations, many=True).data

        return Response(data, status=200)


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    @action(detail=True, methods=["get"])
    def generate_logs(self, request, pk=None):
        trip = self.get_object()
        logs = self.calculate_trip_logs(trip)
        return Response(logs)

    def calculate_trip_logs(self, trip):
        driver = trip.driver
        cycle_hours = 70 if driver.carrier.hos_cycle_choice == "70" else 60
        remaining_hours = max(cycle_hours - driver.current_cycle_used, 0)

        logs = []
        current_time = trip.start_time
        total_driving = 0
        duty_window_start = current_time
        break_accumulator = 0

        while total_driving < trip.estimated_duration.total_seconds() / 3600:
            if remaining_hours <= 0:
                raise ValidationError(
                    "Driver exceeds cycle hours - requires 34hr restart"
                )

            if (current_time - duty_window_start).total_seconds() / 3600 >= 14:
                current_time = duty_window_start + timedelta(hours=14)
                logs.append(self.create_off_duty(current_time, 10))
                duty_window_start = current_time + timedelta(hours=10)
                current_time = duty_window_start
                continue

            max_drive_segment = min(
                11 - (driver.current_cycle_used % 11),
                remaining_hours,
                trip.estimated_duration.total_seconds() / 3600 - total_driving,
                14 - (current_time - duty_window_start).total_seconds() / 3600,
            )

            drive_end = current_time + timedelta(hours=max_drive_segment)
            logs.append(
                {
                    "log_entry": trip.log_entry,
                    "status": "D",
                    "start_time": current_time,
                    "end_time": drive_end,
                    "location_name": "En route",
                }
            )

            total_driving += max_drive_segment
            driver.current_cycle_used += max_drive_segment
            remaining_hours -= max_drive_segment
            current_time = drive_end
            break_accumulator += max_drive_segment

            if break_accumulator >= 8:
                break_time = current_time + timedelta(minutes=30)
                logs.append(
                    {
                        "log_entry": trip.log_entry,
                        "status": "OFF",
                        "start_time": current_time,
                        "end_time": break_time,
                        "location_name": "Rest break",
                    }
                )
                current_time = break_time
                break_accumulator = 0

        driver.save()
        return logs

    def create_off_duty(self, start_time, hours):
        return {
            "log_entry": self.log_entry,
            "status": "OFF",
            "start_time": start_time,
            "end_time": start_time + timedelta(hours=hours),
            "location_name": "Mandatory rest",
        }


class SingleDriverAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        driver = Driver.objects.filter(user=request.user).first()
        if not driver:
            return Response({"error": "No driver found for this user"}, status=404)

        log_entry = LogEntry.objects.filter(driver=driver).first()
        if not log_entry:
            return Response({"error": "No log entry found for this driver"}, status=404)

        data = LogEntrySerializer(log_entry).data
        return Response(data, status=200)


class TripViewSet(viewsets.ModelViewSet):
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated, IsDriverOwner]
    queryset = (
        Trip.objects.select_related("driver__user")
        .prefetch_related("stops")
        .order_by("-start_time")
    )

    def get_queryset(self):
        driver = Driver.objects.filter(user=self.request.user).first()
        if driver is None:
            return Trip.objects.none()
        return self.queryset.filter(driver=driver)

    @transaction.atomic
    def perform_create(self, serializer):
        driver = self.request.user.driver

        if Trip.objects.filter(driver=driver, completed=False).exists():
            raise TripValidationError(
                "Driver already has an active trip. Complete current trip before starting a new one."
            )

        if driver.remaining_hours() <= 0:
            raise TripValidationError("Driver has no remaining hours in current cycle")

        trip = Trip.objects.create(
            driver=driver,
            vehicle_id=self.request.data.get("vehicle"),
            current_location=self.request.data.get("current_location"),
            pickup_location=self.request.data.get("pickup_location"),
            dropoff_location=self.request.data.get("dropoff_location"),
        )

        LogEntry.objects.create(
            driver=driver,
            vehicle=trip.vehicle,
            date=timezone.now().date(),
            start_odometer=0,
            end_odometer=0,
            remarks=f"Initial log entry for trip {trip.id}",
            signature=self.request.user.get_full_name(),
        )

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        trip = self.get_object()

        if trip.completed:
            return Response(
                {"error": "Cannot start a completed trip"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if trip.start_time and trip.start_time > timezone.now():
            return Response(
                {"error": "Trip cannot be started before scheduled time"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        active_trips = Trip.objects.filter(driver=trip.driver, completed=False).exclude(
            pk=trip.pk
        )

        if active_trips.exists():
            return Response(
                {"error": "Driver already has another active trip"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        trip.start_time = timezone.now()
        trip.save()

        if trip.log_entry:
            trip.log_entry.start_odometer = request.data.get("start_odometer", 0)
            trip.log_entry.save()

        return Response(
            {
                "status": "trip started",
                "start_time": trip.start_time,
                "current_location": trip.current_location,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        trip = self.get_object()

        if trip.completed:
            return Response(
                {"error": "Trip already completed"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not trip.start_time or trip.start_time > timezone.now():
            return Response(
                {"error": "Cannot complete a trip that hasn't started"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            trip.completed_at = timezone.now()
            trip.completed = True
            trip.save()

            trip.driver.current_location = trip.dropoff_location
            trip.driver.save()

            if trip.log_entry:
                trip.log_entry.end_odometer = request.data.get("end_odometer", 0)
                trip.log_entry.total_miles = (
                    trip.log_entry.end_odometer - trip.log_entry.start_odometer
                )
                trip.log_entry.save()

        return Response(
            {
                "status": "trip completed",
                "completed_at": trip.completed_at,
                "distance_traveled": (
                    trip.log_entry.total_miles if trip.log_entry else 0
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        throttle_classes=[UserRateThrottle],
        url_path="stops",
    )
    def stops(self, request, pk=None):
        try:
            trip = self.get_object()

            if trip.completed:
                return Response(
                    {"detail": "Cannot generate stops for completed trips"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                fuel_stops = calculate_fuel_stops(
                    trip.distance,
                    trip.start_time,
                    origin=trip.pickup_location,
                    destination=trip.dropoff_location,
                    api_key=settings.MAPS_API_KEY,
                )

                for stop in fuel_stops:
                    Stop.objects.create(
                        trip=self,
                        stop_type=stop.stop_type,
                        location_name=stop.location_name,
                        location_lat=stop.location_lat,
                        location_lon=stop.location_lon,
                        scheduled_time=stop.scheduled_time,
                        duration=stop.duration,
                    )

            serializer = TripSerializer(trip)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error generating stops for trip {pk}: {str(e)}")
            return Response(
                {"detail": "Error generating stops"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        trip = self.get_object()
        serializer = self.get_serializer(trip)

        response_data = {
            **serializer.data,
            "status": (
                "completed"
                if trip.completed
                else "in_progress" if trip.start_time else "scheduled"
            ),
            "stops": StopSerializer(
                trip.stops.order_by("scheduled_time"), many=True
            ).data,
            "driver_remaining_hours": trip.driver.remaining_hours(),
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def active(self, request):
        driver = request.user.driver
        active_trip = Trip.objects.filter(
            driver=driver, completed=False, start_time__lte=timezone.now()
        ).first()

        if not active_trip:
            return Response(
                {"detail": "No active trip found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(active_trip)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def update_location(self, request, pk=None):
        trip = self.get_object()

        if trip.completed:
            return Response(
                {"error": "Cannot update location of completed trip"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_location = request.data.get("current_location")
        if not new_location:
            return Response(
                {"error": "Location data required"}, status=status.HTTP_400_BAD_REQUEST
            )

        trip.current_location = new_location
        trip.save()

        return Response(
            {
                "status": "location updated",
                "current_location": new_location,
                "updated_at": timezone.now(),
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        trip = self.get_object()

        if not trip.completed and trip.start_time and trip.start_time <= timezone.now():
            return Response(
                {"error": "Cannot delete an active trip. Complete it first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)
