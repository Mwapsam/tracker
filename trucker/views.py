from rest_framework import viewsets, serializers, views
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from spotter.settings.serializers import CustomTokenObtainPairSerializer
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
from datetime import timedelta


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
        data = DriverSerializer(driver).data
        return Response(data, status=200)
