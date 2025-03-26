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
        "start_time",
        "get_end_time",
        "get_total_miles",
    )

    def get_end_time(self, obj):
        return obj.end_time if obj.end_time else "N/A"

    get_end_time.admin_order_field = "end_time"
    get_end_time.short_description = "End Time"

    def get_total_miles(self, obj):
        return obj.total_miles if obj.total_miles else "N/A"

    get_total_miles.admin_order_field = "total_miles"
    get_total_miles.short_description = "Total Miles"


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ("trip", "location_name", "get_arrival_time", "get_departure_time")

    def get_arrival_time(self, obj):
        return obj.arrival_time if obj.arrival_time else "N/A"

    get_arrival_time.admin_order_field = "arrival_time"
    get_arrival_time.short_description = "Arrival Time"

    def get_departure_time(self, obj):
        return obj.departure_time if obj.departure_time else "N/A"

    get_departure_time.admin_order_field = "departure_time"
    get_departure_time.short_description = "Departure Time"
