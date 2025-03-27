from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Driver, Carrier, Stop, Trip, Vehicle, LogEntry, DutyStatus


class DutyStatusSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    location = serializers.SerializerMethodField()

    location_lat = serializers.FloatField(write_only=True, required=True)
    location_lon = serializers.FloatField(write_only=True, required=True)
    location_name = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = DutyStatus
        fields = [
            "id",
            "status",
            "status_display",
            "start_time",
            "end_time",
            "location",
            "location_lat",
            "location_lon",
            "location_name",
        ]

    def get_location(self, obj):
        return {
            "lat": obj.location_lat,
            "lon": obj.location_lon,
            "name": obj.location_name,
        }


class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = ["name", "main_office_address", "home_terminal_address"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class DriverSerializer(serializers.ModelSerializer):
    carrier = CarrierSerializer(required=False)
    user = UserSerializer(required=False)

    class Meta:
        model = Driver
        fields = "__all__"
        extra_kwargs = {
            "license_number": {"required": False},
        }


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"
        extra_kwargs = {
            "truck_number": {"required": False},
            "trailer_number": {"required": False},
        }


class LogEntrySerializer(serializers.ModelSerializer):
    duty_statuses = DutyStatusSerializer(many=True, required=False)
    driver = DriverSerializer()
    vehicle = VehicleSerializer()

    class Meta:
        model = LogEntry
        fields = [
            "id",
            "date",
            "vehicle",
            "start_odometer",
            "end_odometer",
            "remarks",
            "signature",
            "duty_statuses",
            "driver",
        ]


class LogEntryCreateSerializer(serializers.ModelSerializer):
    duty_statuses = DutyStatusSerializer(many=True, required=False)

    class Meta:
        model = LogEntry
        fields = [
            "id",
            "date",
            "vehicle",
            "start_odometer",
            "end_odometer",
            "remarks",
            "signature",
            "duty_statuses",
            "driver",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
        }

    def create(self, validated_data):
        duty_statuses_data = validated_data.pop("duty_statuses", [])
        log_entry = LogEntry.objects.create(**validated_data)
        for ds_data in duty_statuses_data:
            DutyStatus.objects.create(log_entry=log_entry, **ds_data)
        return log_entry


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = [
            "id",
            "trip",
            "stop_type",
            "location_name",
            "location_lat",
            "location_lon",
            "scheduled_time",
            "actual_time",
            "duration",
        ]


class TripSerializer(serializers.ModelSerializer):
    stops = StopSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()
    driver_name = serializers.CharField(
        source="driver.user.get_full_name", read_only=True
    )
    remaining_hours = serializers.FloatField(
        source="driver.remaining_hours", read_only=True
    )

    class Meta:
        model = Trip
        fields = [
            "id",
            "driver",
            "driver_name",
            "current_location",
            "pickup_location",
            "dropoff_location",
            "distance",
            "estimated_duration",
            "start_time",
            "completed_at",
            "completed",
            "average_speed",
            "created_at",
            "stops",
            "remaining_hours",
            "status",
        ]
        read_only_fields = [
            "distance",
            "estimated_duration",
            "created_at",
            "stops",
            "remaining_hours",
        ]

    def validate(self, data):
        driver = data.get("driver", getattr(self.instance, "driver", None))
        if not driver:
            raise serializers.ValidationError("Driver is required")

        request = self.context.get("request")
        if request and request.user != driver.user:
            raise serializers.ValidationError("You can only manage your own trips")

        if data.get("start_time") and data["start_time"] < timezone.now():
            raise serializers.ValidationError("Start time must be in the future")

        return data

    def create(self, validated_data):
        return Trip.objects.create(**validated_data)
