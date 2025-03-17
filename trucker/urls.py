from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import LogEntryViewSet, DriverViewSet, VehicleViewSet, CarrierViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


router = DefaultRouter()
router.register(r"logs", LogEntryViewSet, basename="log")
router.register(r"drivers", DriverViewSet)
router.register(r"vehicles", VehicleViewSet)
router.register(r"carriers", CarrierViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
