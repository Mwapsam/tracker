from django.contrib import admin

# admin.py
from django.contrib import admin
from .models import Carrier, Driver, Vehicle, LogEntry, DutyStatus, Trip, Stop


@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ("name", "main_office_address", "home_terminal_address")
    search_fields = ("name",)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("user", "license_number")
    search_fields = ("user__username", "license_number")


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("truck_number", "trailer_number")
    search_fields = ("truck_number", "trailer_number")


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "driver",
        "vehicle",
        "start_odometer",
        "end_odometer",
        "total_miles",
    )
    list_filter = ("date", "driver", "vehicle")


@admin.register(DutyStatus)
class DutyStatusAdmin(admin.ModelAdmin):
    list_display = ("log_entry", "status", "start_time", "end_time", "location_name")
    list_filter = ("status", "location_name")


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        "driver",
        "vehicle",
        "current_location",
        "pickup_location",
        "dropoff_location",
        "distance",
        "estimated_duration",
        "average_speed",
        "start_time",
        "completed_at",
        "completed",
    )


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = (
        "trip",
        "location_name",
        "stop_type",
        "location_lat",
        "location_lon",
        "scheduled_time",
        "actual_time",
        "duration",
    )
