from rest_framework import serializers

from payments.models import Payment
from helpers import functions as f


class PaymentSerializer(serializers.ModelSerializer):
    """serializes payment objects"""
    payment_date = serializers.DateTimeField(required=False)

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ("id", "created_on", "updated_on")

    def create(self, validated_data):
        """creates a new payment obj with validated data"""
        request_user = validated_data.pop("request_user")
        payment_date = validated_data.get("payment_date")
        if not payment_date:
            validated_data["payment_date"] = f.get_current_time()
        validated_data["created_by"] = request_user.id
        validated_data["updated_by"] = request_user.id
        payment = Payment.objects.create(**validated_data)
        return payment

    def update(self, instance, validated_data):
        """updates a payment with validated data"""
        request_user = validated_data.pop("request_user")
        instance.order = validated_data.get("order", instance.order)
        instance.paid_amount = validated_data.get("paid_amount", instance.paid_amount)
        instance.payment_date = validated_data.get("payment_date", instance.payment_date)
        instance.mode_of_payment = validated_data.get("mode_of_payment", instance.mode_of_payment)
        instance.comments = validated_data.get("comments", instance.comments)
        instance.is_deleted = validated_data.get("is_deleted", instance.is_deleted)
        instance.updated_by = request_user.id
        instance.updated_on = validated_data["updated_on"]
        instance.save()
        return instance
