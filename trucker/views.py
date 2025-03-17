from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import LogEntry, Driver, Vehicle, Carrier
from .serializers import (
    LogEntrySerializer,
    DriverSerializer,
    VehicleSerializer,
    CarrierSerializer,
)

class LogEntryViewSet(viewsets.ModelViewSet):
    serializer_class = LogEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LogEntry.objects.filter(driver__user=self.request.user)

    def perform_create(self, serializer):
        driver = Driver.objects.get(user=self.request.user)
        serializer.save(driver=driver)

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