from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.contrib.auth import get_user_model
from django.conf import settings
from datetime import datetime

from rest_framework.decorators import api_view, permission_classes,\
    authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
import jwt

from account.serializers import UserSerializer
from core.authentication import generate_access_token, generate_refresh_token
from core.serializers import AuthTokenSerializer
from account.permissions import IsOwner
from account.models import Business, UserProfile
from account.serializers import BusinessSerializer, UserProfileReadOnlySerializer


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login_view(request):
    """view to log in user"""
    auth_serializer = AuthTokenSerializer(data=request.data)
    auth_serializer.is_valid(raise_exception=True)
    email = auth_serializer.data.get("email", None)
    username = auth_serializer.data.get("username", None)
    user = None
    serialized_user = None
    if email:
        user = get_user_model().objects.filter(email=email).first()
        serialized_user = UserSerializer(user).data
    elif username:
        user = get_user_model().objects.filter(username=username).first()
        serialized_user = UserSerializer(user).data

    access_token = generate_access_token(serialized_user)
    refresh_token = generate_refresh_token(serialized_user)
    response = Response()
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    response.data = {
        "access_token": access_token,
        "user": serialized_user,
    }
    if user.business:
        business = Business.objects.filter(id=user.business.id).first()
        business_data = BusinessSerializer(business).data
        response.data["user"]["business"] = business_data

    profile = UserProfile.objects.filter(user=user.id).first()
    if profile:
        response.data["user"]["profile"] = UserProfileReadOnlySerializer(profile).data
    return response


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@csrf_protect
def get_access_token(request):
    """returns access token for valid refresh token"""
    refresh_token = request.COOKIES.get("refresh_token")
    if not refresh_token:
        raise AuthenticationFailed("Authentication details are not provided")

    try:
        jwt_payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Refresh token is invalid")

    if jwt_payload["expire_time"] <= datetime.utcnow().timestamp() * 1000:
        raise AuthenticationFailed("Refresh token is invalid")

    user = get_user_model().objects.filter(pk=jwt_payload["user_id"]).first()
    if not user:
        raise AuthenticationFailed("User not found")
    elif not user.is_active:
        raise AuthenticationFailed("User is inactive")

    user = UserSerializer(user).data
    access_token = generate_access_token(user)
    return Response(
        {
            "access_token": access_token
        },
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def activate_user(request):
    """activates user"""
    email = request.data.get("email", None)
    username = request.data.get("username", None)
    if not email and not username:
        detail = {
            "message": "Username or email is required to activate user"
        }
        return Response(detail, status=status.HTTP_400_BAD_REQUEST)

    user = None
    if username:
        user = get_user_model().objects.filter(username=username, is_active=False).first()
    elif email:
        user = get_user_model().objects.filter(email=email, is_active=False).first()

    if not user:
        detail = {
            "message": "User with provided credentials is not found or user might be active"
        }
        return Response(detail, status=status.HTTP_400_BAD_REQUEST)
    if user.user_role == "business_staff":
        detail = {
            "message": "Staff user cannot be activated. Please contact admin"
        }
        return Response(detail, status=status.HTTP_400_BAD_REQUEST)

    user.is_active = True
    user.save()
    detail = {
        "message": "User is active. Please login"
    }
    return Response(detail, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsOwner])
def activate_staff(request):
    """activates staff user"""
    username = request.data.get("username", None)
    email = request.data.get("email", None)
    if not username and not email:
        detail = {
            "message": "Username or email is required to activate user"
        }
        return Response(detail, status=status.HTTP_400_BAD_REQUEST)

    user = None
    if username:
        user = get_user_model().objects.filter(username=username, is_active=False).first()
    elif email:
        user = get_user_model().objects.filter(email=email, is_active=False).first()

    if not user:
        detail = {
            "message": "User with provided credentials is not found or user might be active"
        }
        return Response(detail, status=status.HTTP_400_BAD_REQUEST)

    if (request.user.user_role == "business_admin" and \
            request.user.business == user.business) or request.user.is_superuser:
        user.is_active = True
        user.save()
        detail = {
            "message": "User is active. Please login"
        }
        return Response(detail, status=status.HTTP_200_OK)

    detail = {
        "message": "Unauthorized to activate staff user."
    }
    return Response(detail, status=status.HTTP_401_UNAUTHORIZED)

