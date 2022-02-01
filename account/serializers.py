from django.contrib.auth import get_user_model, authenticate

from rest_framework import serializers

from account import models

class UserSerializer(serializers.ModelSerializer):
    """serializes user objects"""

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "user_role", "password", "is_active")
        read_only_fields = ("id",)
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        """Creates a new user with validated data"""
        request_user = validated_data.get("request_user")
        validated_data["is_active"] = True
        if request_user:
            validated_data.pop("request_user")
            validated_data["created_by"] = request_user.id
            validated_data["updated_by"] = request_user.id
        user = get_user_model().objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """updates a user object in DB"""
        request_user = validated_data.pop("request_user")
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.user_role = validated_data.get("user_role", instance.user_role)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.is_superuser = validated_data.get("is_superuser", instance.is_superuser)
        instance.updated_on = validated_data["updated_on"]
        instance.updated_by = request_user.id
        password = validated_data.get("password", None)
        if password is not None:
            instance.set_password(validated_data["password"])
        instance.save()
        return instance


class BusinessSerializer(serializers.ModelSerializer):
    """serializes the business objects"""

    class Meta:
        model = models.Business
        fields = ("id", "name", "staff_count", "max_staff_count")
        read_only_fields = ("id",)

    def create(self, validated_data):
        """creates a new business obj with validated data"""
        request_user = validated_data.get("request_user")
        if request_user:
            validated_data["created_by"] = request_user.id
            validated_data["updated_by"] = request_user.id
        business = models.Business.objects.create(**validated_data)
        return business

    def update(self, instance, validated_data):
        """updates a business object with validated data"""
        request_user = validated_data.pop("request_user")
        instance.name = validated_data.get("name", instance.name)
        instance.staff_count = validated_data.get("staff_count", instance.staff_count)
        instance.max_staff_count = validated_data.get("max_staff_count",
                                                      instance.max_staff_count)
        instance.updated_by = request_user.id
        instance.updated_on = validated_data["updated_on"]
        instance.save()
        return instance
