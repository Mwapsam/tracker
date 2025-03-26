from rest_framework import viewsets, views
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from spotter.settings.serializers import CustomTokenObtainPairSerializer
from trucker.exceptions import TripValidationError
from trucker.permissions import IsDriverOwner
from .models import DutyStatus, LogEntry, Driver, Trip, Vehicle, Carrier
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
from .services.hos_services import generate_hos_logs


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
        return Trip.objects.filter(driver=driver)

    @transaction.atomic
    def perform_create(self, serializer):
        trip = serializer.save()
        trip.log_entry = LogEntry.objects.create(driver=trip.driver)
        trip.save()

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        """Mark trip as started"""
        trip = self.get_object()

        if trip.completed:
            return Response(
                {"error": "Cannot start a completed trip"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if trip.start_time > timezone.now():
            return Response(
                {"error": "Trip cannot be started before scheduled time"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        trip.start_time = timezone.now()
        trip.save()
        return Response(
            {"status": "trip started", "start_time": trip.start_time},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        trip = self.get_object()
        if trip.completed:
            return Response(
                {"error": "Trip already completed"}, status=status.HTTP_400_BAD_REQUEST
            )

        trip.completed_at = timezone.now()
        trip.completed = True
        trip.save()

        trip.driver.current_location = trip.dropoff_location
        trip.driver.save()

        return Response(
            {"status": "trip completed", "completed_at": trip.completed_at},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    def logs(self, request, pk=None):
        try:
            trip = self.get_object()
            logs = generate_hos_logs(trip)
            return Response(logs, status=status.HTTP_200_OK)
        except TripValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Failed to generate logs"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    def route_details(self, request, pk=None):
        trip = self.get_object()
        serializer = self.get_serializer(trip)
        return Response(
            {
                **serializer.data,
                "stops": StopSerializer(
                    trip.stops.order_by("scheduled_time"), many=True
                ).data,
            }
        )

    @action(detail=False, methods=["get"])
    def active(self, request):
        active_trips = self.get_queryset().filter(
            start_time__lte=timezone.now(), completed=False
        )
        serializer = self.get_serializer(active_trips, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def update_location(self, request, pk=None):
        trip = self.get_object()
        new_location = request.data.get("current_location")

        if not new_location:
            return Response(
                {"error": "Location data required"}, status=status.HTTP_400_BAD_REQUEST
            )

        trip.current_location = new_location
        trip.save()
        return Response(
            {"status": "location updated", "current_location": new_location},
            status=status.HTTP_200_OK,
        )
