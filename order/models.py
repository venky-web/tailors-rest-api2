from django.db import models

from user.models import User


class Order(models.Model):
    """Model to manage orders"""
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    delivery_date = models.DateTimeField()
    order_status = models.CharField(max_length=64)
    comments = models.TextField(max_length=1024, default="", blank=True)
    is_one_time_delivery = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField()
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)
    is_deleted = models.CharField(max_length=1, default="N")

    class Meta:
        ordering = ("-created_on",)

    def __str__(self):
        """string representation of order item"""
        return f"{self.id}"


class OrderItem(models.Model):
    """Model to manage order item"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name="order_items", related_query_name="order_item")
    item_type = models.CharField(max_length=255)
    item_price = models.DecimalField(max_digits=7, decimal_places=2)
    quantity = models.IntegerField()
    status = models.CharField(max_length=64)
    delivery_date = models.DateTimeField()
    comments = models.TextField(max_length=512, default="", blank=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField()
    is_deleted = models.CharField(max_length=1, default="N")

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        """string representation of order item"""
        return f"{self.id}"
