from rest_framework.permissions import BasePermission, SAFE_METHODS

from account.models import Business, UserBusinessRelation


class IsOwner(BasePermission):
    """checks if user has permission to the obj"""
    def has_object_permission(self, request, view, obj):
        """returns True if user has permission for the obj"""
        if request.user.is_superuser:
            return True
        return obj.id == request.user.id


class IsOwnerOrReadOnly(BasePermission):
    """checks if user has write access or only read access"""

    def has_object_permission(self, request, view, obj):
        """returns True if user has write access"""
        if request.user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return True

        return request.user.id == obj.id


class IsBusinessAdmin(BasePermission):
    """checks if user is a business admin"""
    def has_permission(self, request, view):
        """returns True if user is business admin"""
        return request.user.is_superuser or request.user.user_role == "business_admin"

    def has_object_permission(self, request, view, obj):
        """returns True if user is business admin"""
        if request.user.is_superuser:
            return True

        return request.user.user_role == "business_admin"


class IsBusinessAdminOrStaff(BasePermission):
    """checks if user is a business admin or business staff"""
    def has_permission(self, request, view):
        """returns True if user is a business admin or staff"""
        if request.user.is_superuser:
            return True

        return request.user.user_role == "business_admin" or \
               request.user.user_role == "business_staff"

    def has_object_permission(self, request, view, obj):
        """returns True if user is a business admin or staff or owner"""
        if request.user.is_superuser:
            return True

        if request.user.user_role == "business_admin" or \
            request.user.user_role == "business_staff":
            return True

        return False


class MaxStaffCount(BasePermission):
    """checks if max staff count is reached"""
    message = "Staff limit is reached. Cannot add staff user."

    def has_permission(self, request, view):
        """returns True if staff count is less than max staff count"""
        if request.method in SAFE_METHODS:
            return True

        business = None
        if request.user.is_superuser:
            business_id = request.data.get("business")
            business = Business.objects.filter(id=business_id).first()
        elif request.user.business:
            business = request.user.business

        if business:
            return business.staff_count < business.max_staff_count
        return False


class IsOwnBusiness(BasePermission):
    """checks if user belongs to same business"""

    def has_object_permission(self, request, view, obj):
        """returns True if user is a business admin or staff or owner"""
        if request.user.is_superuser:
            return True

        if not request.user.business or not obj.business:
            return False

        return request.user.business.id == obj.business.id


class ReadOnlyAccessToStaff(BasePermission):
    """checks if user is staff and request method is safe """
    def has_permission(self, request, view):
        """returns True if user is staff and request method is in safe methods list"""
        if request.user.is_superuser:
            return True

        if request.user.user_role == "business_admin":
            return True

        return request.user.user_role == "business_staff" and \
               request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        """returns True if user is staff and request method is in safe methods list"""
        if request.user.is_superuser:
            return True

        if request.user.user_role == "business_admin":
            return True

        return request.user.user_role == "business_staff" and \
               request.method in SAFE_METHODS


class IsOwnerOrBusinessAdmin(BasePermission):
    """checks if user is owner of object or business admin"""
    def has_object_permission(self, request, view, obj):
        """returns True if user is owner of obj or business admin"""
        if request.user.is_superuser:
            return True

        if request.user.user_role == "business_admin":
            return True

        return request.user.id == obj.id


class BusinessAdminOrStaffWithOwnBusiness(BasePermission):
    """checks whether user is business admin or superuser"""
    def has_object_permission(self, request, view, obj):
        """returns true if user has permission to view/edit/delete the obj"""
        if request.user.is_superuser:
            return True

        return (request.user.user_role == "business_admin" or request.user.user_role == "business_staff") and \
               request.user.business and \
               request.user.business.id == obj.id


class IsBusinessAdminOrStaffWithRelation(BasePermission):
    """checks if user is a business admin or business staff"""
    def has_permission(self, request, view):
        """returns True if user is a business admin or staff"""
        if request.user.is_superuser:
            return True

        return request.user.user_role == "business_admin" or \
               request.user.user_role == "business_staff"

    def has_object_permission(self, request, view, obj):
        """returns True if user is a business admin or staff or owner"""
        if request.user.is_superuser:
            return True

        if request.user.user_role == "business_admin" or \
            request.user.user_role == "business_staff":

            relation = UserBusinessRelation.objects.filter(user_id=obj.id,
                                                           business_id=request.user.business.id).first()

            return relation and relation.request_status == "Approved"

        return False
