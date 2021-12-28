from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from datetime import datetime

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """serializes user objects"""

    class Meta:
        model = get_user_model()
        fields = "__all__"
        exclude = ("is_admin",)
        read_only_fields = ("id", "created_on", "updated_on", "created_by", "updated_by")
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        """Creates a new user with validated data"""
        validated_data["updated_on"] = datetime.now().strftime(
            "%Y-%m-%dT%H:%M:%S%z")
        return get_user_model().objects.create(**validated_data)

    def update(self, instance, validated_data):
        """updates a user object in DB"""
        instance.email = validated_data.get("'email", instance.email)
        instance.first_name = validated_data.get("first_name",
                                                 instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.user_type = validated_data.get("user_type", instance.user_type)
        instance.updated_on = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
        instance.is_active = validated_data.get("is_active",
                                                instance.is_active)
        instance.set_password(validated_data["password"])
        instance.save()

        return instance