from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """checks if user has permission for obj"""
    def has_object_permission(self, request, view, obj):
        """returns True if user has permission for the obj"""
        if request.user.is_superuser:
            return True

        if request.user.user_role == "business_admin" and \
            request.user.business == obj.business:
            return True

        return obj.id == request.user.id

    def has_permission(self, request, view):
        """returns True if user has permission for the view"""
        if request.user.is_superuser:
            return True

        if request.user.user_role == "business_admin":
            return True

        return False
