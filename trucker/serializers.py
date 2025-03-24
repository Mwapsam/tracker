from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Driver, Carrier, Vehicle, LogEntry, DutyStatus


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
