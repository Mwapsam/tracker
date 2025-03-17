from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import LogEntryViewSet, DriverViewSet, VehicleViewSet, CarrierViewSet

router = DefaultRouter()
router.register(r"logs", LogEntryViewSet, basename="log")
router.register(r"drivers", DriverViewSet)
router.register(r"vehicles", VehicleViewSet)
router.register(r"carriers", CarrierViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
