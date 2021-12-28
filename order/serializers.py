from datetime import datetime

from rest_framework import serializers

from order import models


class OrderSerializer(serializers.ModelSerializer):
    """serializes order model objects"""
    created_by = serializers.CharField(required=False)
    updated_by = serializers.CharField(required=False)
    updated_on = serializers.DateTimeField(required=False)

    class Meta:
        model = models.Order
        fields = "__all__"
        read_only_fields = ("created_by", "updated_by", "updated_on", "created_on")

    def create(self, validated_data):
        """Creates a new order object in db"""
        validated_data["updated_on"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        else:
            user = validated_data.pop("user")
        validated_data["created_by"] = user.id
        validated_data["updated_by"] = user.id
        order = models.Order.objects.create(**validated_data)
        return order

    def update(self, instance, validated_data):
        """updates an order object with validated data"""
        instance.customer_id = validated_data.get("'customer_id", instance.customer_id)
        instance.total_amount = validated_data.get("total_amount", instance.total_amount)
        instance.delivery_date = validated_data.get("delivery_date", instance.delivery_date)
        instance.order_status = validated_data.get("order_status", instance.order_status)
        instance.comments = validated_data.get("comments", instance.comments)
        instance.is_one_time_delivery = validated_data.get("is_one_time_delivery",
                                                           instance.is_one_time_delivery)
        instance.updated_on = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        else:
            user = validated_data.pop("user")
        instance.updated_by = user.id
        instance.save()
        return instance


class OrderItemSerializer(serializers.ModelSerializer):
    """serializes order item objects"""
    class Meta:
        model = models.OrderItem
        fields = "__all__"
