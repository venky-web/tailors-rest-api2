from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from core.authentication import generate_access_token, generate_refresh_token
from account import serializers, models
from helpers import functions as helpers


def update_business_staff_count(business_id, add_staff=1, operation="add"):
    """updates staff count of business
        Args: business_id, add_staff=1, operation="add"
    """
    business_instance = get_object_or_404(Business, pk=business_id)
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
                "message": "User with provided username already exists"
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


def add_tokens(response, user):
    """adds refresh and access tokens to the response"""
    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    response.data["access_token"] =  access_token
    return response


def save_user_profile(request, user, profile=None):
    """saves user profile
        Args: request, user, profile (default=None)
    """
    global serializer
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
