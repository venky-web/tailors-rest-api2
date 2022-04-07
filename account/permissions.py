from django.contrib.auth import get_user_model

from rest_framework.permissions import BasePermission, SAFE_METHODS

from account.models import Business, UserBusinessRelation


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

        if request.user.user_role == "business_admin" and request.user.business:
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


class IsBusinessAdminOrSuperuser(BasePermission):
    """checks whether user is business admin or superuser"""
    def has_permission(self, request, view):
        """returns true if user has permission to the view"""
        if request.user.is_superuser:
            return True

        return request.user.user_role == "business_admin"

    def has_object_permission(self, request, view, obj):
        """returns true if user has permission to view/edit/delete the obj"""
        if request.user.is_superuser:
            return True

        return request.user.user_role == "business_admin" and \
               request.user.business and \
               request.user.business.id == obj.id


class IsBusinessAdminOrStaff(BasePermission):
    """checks whether user is business admin, staff or superuser"""
    def has_permission(self, request, view):
        """returns true if user has permission to the view"""
        if request.user.is_superuser:
            return True

        return request.user.user_role == "business_admin" or request.user.user_role == "business_staff"


class IsUpdateProfile(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if request.user.user_role == "business_admin" or request.user.user_role == "business_staff":
            return True

        return request.user == get_user_model().objects.filter(pk=view.kwargs['id']).first()

    def has_object_permission(self, request, view, obj):
        """returns true if user has permission to view/edit/delete the obj"""
        if request.user.is_superuser:
            return True

        if (request.user.user_role == "business_admin" or request.user.user_role == "business_staff") \
            and request.user.id != obj.id:
            user_business_relation = UserBusinessRelation.objects.filter(business_id=request.user.business.id,
                                                                         user_id=obj.id).first()
            return user_business_relation and user_business_relation.request_status == "Approved"

        return request.user.id == obj.id
