from rest_framework import viewsets, serializers, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DutyStatus, LogEntry, Driver, Vehicle, Carrier
from .serializers import (
    DutyStatusSerializer,
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
        return LogEntry.objects.all()

    def perform_create(self, serializer):
        try:
            driver = Driver.objects.get(user=self.request.user)
        except Driver.DoesNotExist:
            raise serializers.ValidationError(
                "Driver profile does not exist for this user."
            )
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
