from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.exceptions import NotFound

from core.authentication import generate_access_token, generate_refresh_token
from account import serializers, models
from helpers import functions as helpers


def update_business_staff_count(business_id, add_staff=1, operation="add"):
    """updates staff count of business
        Args: business_id, add_staff=1, operation="add"
    """
    business_instance = get_object_or_404(models.Business, pk=business_id)
    if operation == "add":
        business_instance.staff_count += add_staff
    elif operation == "delete":
        business_instance.staff_count -= add_staff
    business_instance.save()
    return business_instance


def check_for_username_password(request):
    """check for username and password in payload"""
    username = request.data.get("username", None)
    if username:
        user = get_user_model().objects.filter(username=username).first()
        if user and user.is_active == False:
            error = {
                "message": "User is inactive"
            }
            return Response(error, status=HTTP_400_BAD_REQUEST)
        elif user:
            error = {
                "message": "Username already exists"
            }
            return Response(error, status=HTTP_400_BAD_REQUEST)
    else:
        error = {
            "message": "Username or password is missing"
        }
        return Response(error, status=HTTP_400_BAD_REQUEST)

    email = request.data.get("email", None)
    if email:
        user = get_user_model().objects.filter(email=email).first()
        if user:
            error = {
                "message": "User with provided email already exists"
            }
            return Response(error, status=HTTP_400_BAD_REQUEST)


def get_users(queryset):
    """returns list of users"""
    response_data = []
    for user in queryset.iterator():
        user_data = serializers.UserSerializer(user).data.copy()
        user_profile = models.UserProfile.objects.filter(user=user.id).first()
        if user_profile:
            user_data["profile"] = serializers.UserProfileReadOnlySerializer(user_profile).data.copy()
        if user.user_role == "business_admin" or user.user_role == "business_staff":
            business_data = models.Business.objects.filter(pk=user.business.id).first()
            if business_data:
                user_data["business"] = serializers.BusinessSerializer(business_data).data.copy()
        response_data.append(user_data)
    return response_data


def add_tokens(response, user):
    """adds refresh and access tokens to the response"""
    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    response.data["access_token"] =  access_token
    response.data["refresh_token"] = refresh_token,
    return response


def save_user_profile(request, user, profile=None):
    """saves user profile
        Args: request, user, profile (default=None)
    """
    # global serializer
    if profile is not None:
        serializer = serializers.UserProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(
            request_user=request.user,
            updated_on=helpers.get_current_time()
        )
    else:
        request_data = request.data.copy()
        request_data["user"] = user.id
        serializer = serializers.UserProfileSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            request_user=request.user,
            created_on=helpers.get_current_time(),
            updated_on=helpers.get_current_time(),
        )
    return serializer.data


def get_user_profile_and_business_data(user):
    """returns user profile and business data if exists
        Args: user data
    """
    if user["user_role"] == "business_admin" or user["user_role"] == "business_staff":
        user_obj = models.User.objects.filter(pk=user["id"]).first()
        business = models.Business.objects.filter(pk=user_obj.business.id).first()
        user["business"] = serializers.BusinessSerializer(business).data
    profile = models.UserProfile.objects.filter(user=user["id"]).first()
    if profile:
        user["profile"] = serializers.UserProfileReadOnlySerializer(profile).data
    return user


def get_user_data_for_business(request, user):
    """returns user profile and business data if exists
        Args: request, user
    """
    if user["user_role"] == "business_admin" or user["user_role"] == "business_staff":
        user_obj = models.User.objects.filter(pk=user["id"]).first()
        business = models.Business.objects.filter(pk=user_obj.business.id).first()
        user["business"] = serializers.BusinessSerializer(business).data
    profile = models.UserProfile.objects.filter(user=user["id"]).first()
    if profile:
        serialized_profile = serializers.CustomerProfileSerializer(profile).data
        relation = models.UserBusinessRelation.objects.filter(user_id=user["id"],
                                                              business_id=request.user.business.id).first()
        if relation and relation.request_status != "Approved":
            serialized_profile["phone"] = "xxx"
            serialized_profile["date_of_birth"] = None
            serialized_profile["marital_status"] = "xxx"
        user["profile"] = serialized_profile
    return user


def add_user_business_relation(business_id, user_id, comments, status="Pending", expires_in=7):
    """creates a relation between user and business
        Args: user_id, business_id, status='Pending', expires_in=7 (Days)
    """
    user = get_user_model().objects.filter(pk=user_id).first()
    if not user:
        error = {
            "message": "User not found"
        }
        raise NotFound(detail=error, code=404)
    business = models.Business.objects.filter(pk=business_id).first()
    if not business:
        error = {
            "message": "Business not found"
        }
        raise NotFound(detail=error, code=404)

    expires_in = datetime.utcnow() + timedelta(days=expires_in)
    user_request = models.UserBusinessRelation.objects.create(
        user_id=user.id,
        business_id=business_id,
        request_status=status,
        request_date=helpers.get_current_time(),
        updated_date=helpers.get_current_time(),
        request_expiry_date=expires_in.isoformat(),
        comments=comments
    )
    return user_request
