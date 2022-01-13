from datetime import datetime

from rest_framework import serializers

from order import models
from helpers import functions as f


def update_order(user, order):
    """
        Updates order updated_by, updated_on columns
        Args: User, Order
    """
    order.updated_by = user.id
    order.updated_on = f.get_current_time()
    order.save()


class OrderSerializer(serializers.ModelSerializer):
    """serializes order model objects"""
    created_by = serializers.CharField(required=False)
    updated_by = serializers.CharField(required=False)
    delivery_date = serializers.CharField(required=False)

    class Meta:
        model = models.Order
        fields = "__all__"
        read_only_fields = ("id", "created_by", "updated_by", "updated_on", "created_on")

    def create(self, validated_data):
        """Creates a new order object in db"""
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            validated_data.pop("request_user")
        else:
            user = validated_data.pop("request_user")
        validated_data["created_by"] = user.id
        validated_data["updated_by"] = user.id
        validated_data["is_one_time_delivery"] = True
        order = models.Order.objects.create(**validated_data)
        return order

    def update(self, instance, validated_data):
        """updates an order object with validated data"""
        instance.customer = validated_data.get("'customer", instance.customer)
        instance.total_amount = validated_data.get("total_amount", instance.total_amount)
        instance.net_amount = validated_data.get("net_amount", instance.net_amount)
        instance.paid_amount = validated_data.get("paid_amount", instance.paid_amount)
        instance.discount = validated_data.get("discount", instance.discount)
        instance.delivery_date = validated_data.get("delivery_date", instance.delivery_date)
        instance.order_status = validated_data.get("order_status", instance.order_status)
        instance.comments = validated_data.get("comments", instance.comments)
        instance.is_deleted = validated_data.get("is_deleted", instance.is_deleted)
        instance.is_one_time_delivery = validated_data.get("is_one_time_delivery",
                                                           instance.is_one_time_delivery)
        instance.updated_on = validated_data["updated_on"]
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            validated_data.pop("request_user")
        else:
            user = validated_data.pop("request_user")
        instance.updated_by = user.id
        instance.save()
        return instance


class OrderItemSerializer(serializers.ModelSerializer):
    """serializes order item objects"""
    class Meta:
        model = models.OrderItem
        fields = "__all__"
        read_only_fields = ("id", "created_by", "updated_by", "created_on", "updated_on",
                            "order")

    def create(self, validated_data):
        """creates a new order item in db"""
        order = validated_data.get("order")
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            request_user = request.user
            validated_data.pop("request_user")
        else:
            request_user = validated_data.pop("request_user")

        validated_data["created_by"] = request_user.id
        validated_data["updated_by"] = request_user.id
        validated_data["order"] = order
        order_item = models.OrderItem.objects.create(**validated_data)
        update_order(request_user, order)

        return order_item

    def update(self, instance, validated_data):
        """updates an order item in db and order items list"""
        order = validated_data["order"]
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            request_user = request.user
        else:
            request_user = validated_data.pop("request_user")

        instance.order = validated_data.get("order", instance.order)
        instance.item_type = validated_data.get("item_type", instance.item_type)
        instance.item_price = validated_data.get("item_price", instance.item_price)
        instance.quantity = validated_data.get("quantity", instance.quantity)
        instance.status = validated_data.get("status", instance.status)
        instance.delivery_date = validated_data.get("delivery_date", instance.delivery_date)
        instance.comments = validated_data.get("comments", instance.comments)
        instance.is_deleted = validated_data.get("is_deleted", instance.is_deleted)
        instance.updated_by = request_user.id
        instance.updated_on = validated_data["updated_on"]
        instance.save()
        update_order(request_user, order)

        return instance
