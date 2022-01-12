from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.contrib.auth import get_user_model
from django.conf import settings
from datetime import datetime

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
import jwt

from account.serializers import UserSerializer
from core.authentication import generate_access_token, generate_refresh_token
from core.serializers import AuthTokenSerializer


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login_view(request):
    """view to log in user"""
    auth_serializer = AuthTokenSerializer(data=request.data)
    if not auth_serializer.is_valid():
        return Response(auth_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = auth_serializer.data["email"]
    user = get_user_model().objects.filter(email=email).first()
    user = UserSerializer(user).data

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)
    response = Response()
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    response.data = {
        "access_token": access_token,
        "user": user,
    }
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
