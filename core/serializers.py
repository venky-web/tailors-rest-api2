from django.contrib.auth import authenticate

from rest_framework import serializers


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for auth token"""
    email = serializers.EmailField(required=False)
    username = serializers.CharField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validates serialized data"""
        email = attrs.get("email")
        username = attrs.get("username")
        password = attrs.get("password")
        user = None
        if email:
            user = authenticate(
                request=self.context.get("request"),
                username=email,
                password=password
            )
        elif username:
            user = authenticate(
                request=self.context.get("request"),
                username=username,
                password=password
            )

        if not user:
            error = {
                "message": "Unable to authenticate with provided credentials"
            }
            raise serializers.ValidationError(error, code="authentication")

        attrs["user"] = user
        return attrs
