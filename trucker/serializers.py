from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Driver, Carrier, Vehicle, LogEntry, DutyStatus


class DutyStatusSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    location = serializers.SerializerMethodField()

    class Meta:
        model = DutyStatus
        fields = ["status", "status_display", "start_time", "end_time", "location"]

    def get_location(self, obj):
        return {
            "lat": obj.location_lat,
            "lon": obj.location_lon,
            "name": obj.location_name,
        }


class LogEntrySerializer(serializers.ModelSerializer):
    duty_statuses = DutyStatusSerializer(many=True)

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
        ]

    def create(self, validated_data):
        duty_statuses_data = validated_data.pop("duty_statuses")
        log_entry = LogEntry.objects.create(**validated_data)
        for status_data in duty_statuses_data:
            DutyStatus.objects.create(log_entry=log_entry, **status_data)
        return log_entry


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ["truck_number", "trailer_number"]


class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = ["name", "main_office_address", "home_terminal_address"]


class DriverSerializer(serializers.ModelSerializer):
    carrier = CarrierSerializer()

    class Meta:
        model = Driver
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
