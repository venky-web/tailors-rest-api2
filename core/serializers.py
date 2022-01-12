from django.contrib.auth import authenticate, get_user_model

from rest_framework import serializers


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validates serialized data"""
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password
        )

        if not user:
            error = {
                "message": "Unable to authenticate with provided credentials"
            }
            raise serializers.ValidationError(error, code="authentication")

        attrs["user"] = user
        return attrs
