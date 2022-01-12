from django.db import models

from order.models import Order
from core.models import CustomBaseClass


class Payment(CustomBaseClass):
    """payment model in db"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments",
                              related_query_name="payment")
    paid_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    payment_date = models.DateTimeField()
    mode_of_payment = models.CharField(max_length=50, default="cash")
    comments = models.TextField(max_length=200, default="", blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "t_payment"
        ordering = ("-payment_date",)

    def __str__(self):
        """string representation of payment"""
        return f"{self.order} - {self.paid_amount}"
