from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model

import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


def generate_access_token(user):
    """generates access token for the provided user"""
    expire_time = datetime.utcnow() + timedelta(days=0, minutes=30)
    utc_time = datetime.utcnow()
    access_token_payload = {
        "user_id": user["id"],
        "expire_time": expire_time.timestamp() * 1000,
        "iat": utc_time.timestamp() * 1000
    }
    access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm="HS256")
    return access_token


def generate_refresh_token(user):
    """generates a refresh token for the provided user"""
    expire_time = datetime.utcnow() + timedelta(days=1)
    utc_time = datetime.utcnow()
    refresh_token_payload = {
        "user_id": user["id"],
        "expire_time": expire_time.timestamp() * 1000,
        "iat": utc_time.timestamp() * 1000
    }
    refresh_token = jwt.encode(refresh_token_payload, settings.SECRET_KEY, algorithm="HS256")
    return refresh_token


class JWTAuthentication(BaseAuthentication):
    """Authenticates a user with provided credentials"""
    def authenticate(self, request):
        auth_headers = request.headers.get("Authorization")
        if not auth_headers:
            return None

        try:
            access_token = auth_headers.split(" ")[1]
            jwt_payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Invalid authentication credentials")
        except jwt.InvalidSignatureError:
            raise AuthenticationFailed("Invalid authentication credentials")
        except IndexError:
            raise AuthenticationFailed("Access token is not provided")

        if jwt_payload["expire_time"] <= datetime.utcnow().timestamp() * 1000:
            raise AuthenticationFailed("Access token is expired")

        user = get_user_model().objects.filter(pk=jwt_payload["user_id"]).first()
        if not user:
            raise AuthenticationFailed("User not found")

        if not user.is_active:
            raise AuthenticationFailed("User is inactive")

        return user, None

