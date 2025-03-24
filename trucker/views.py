from rest_framework import viewsets, serializers, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DutyStatus, LogEntry, Driver, Vehicle, Carrier
from .serializers import (
    DutyStatusSerializer,
    LogEntryCreateSerializer,
    LogEntrySerializer,
    DriverSerializer,
    UserSerializer,
    VehicleSerializer,
    CarrierSerializer,
)


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
