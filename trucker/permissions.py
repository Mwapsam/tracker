from rest_framework import permissions


class IsDriverOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.driver.user == request.user
