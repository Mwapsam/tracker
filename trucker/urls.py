from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    CurrentUserAPIView,
    CustomTokenObtainPairView,
    DutyStatusViewSet,
    LatestStationsViewSet,
    LogEntryViewSet,
    DriverViewSet,
    VehicleViewSet,
    CarrierViewSet,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


router = DefaultRouter()
router.register(r"logs", LogEntryViewSet, basename="log")
router.register(r"drivers", DriverViewSet)
router.register(r"vehicles", VehicleViewSet)
router.register(r"carriers", CarrierViewSet)
router.register(r"duty-status", DutyStatusViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/current-user/", CurrentUserAPIView.as_view(), name="current-user"),
    path(
        "api/latest-stations/<int:driver_id>/",
        LatestStationsViewSet.as_view(),
        name="latest-stations",
    ),
]
