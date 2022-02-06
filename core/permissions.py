from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProductSeller(BasePermission):
    """Checks if the request user is the owner of the obj"""
    def has_object_permission(self, request, view, obj):
        """returns true if user has permission to the obj"""
        return obj.id == request.user.id
