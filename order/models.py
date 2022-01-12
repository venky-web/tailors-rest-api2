from django.db import models
from django.conf import settings

from core.models import CustomBaseClass


class Order(CustomBaseClass):
    """Model to manage orders"""
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                 null=True)
    total_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    delivery_date = models.DateTimeField()
    order_status = models.CharField(max_length=64, default="Not yet started")
    comments = models.TextField(max_length=1024, default="", blank=True)
    is_one_time_delivery = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "t_order"
        ordering = ("-created_on",)

    def __str__(self):
        """string representation of order item"""
        return f"{self.customer}"


class OrderItem(CustomBaseClass):
    """Model to manage order item"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name="order_items", related_query_name="order_item")
    item_type = models.CharField(max_length=255)
    item_price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=64, default="Not yet started")
    delivery_date = models.DateTimeField()
    comments = models.TextField(max_length=512, default="", blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "t_order_item"
        ordering = ("-id",)

    def __str__(self):
        """string representation of order item"""
        return f"{self.item_type}"
