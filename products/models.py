from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid
import os

from core.models import CustomBaseClass


def image_file_path(instance, filename):
    """returns image path"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("product-images", filename)


class Product(CustomBaseClass):
    """model for product and service"""
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, related_name="product")
    name = models.CharField(_("Name"), max_length=255, unique=True)
    description = models.TextField(max_length=500, default="", blank=True)
    image = models.ImageField(upload_to=image_file_path, null=True)
    category = models.CharField(max_length=255, default="")
    units_available = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    product_code = models.CharField(max_length=255, unique=True)
    is_service = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = "t_product"
        ordering = ("-updated_on",)

    def __str__(self):
        """returns string representation of product"""
        return f"{self.name}"

    def get_product_code(self):
        """returns product code"""
        return f"{self.product_code}"


class ProductDesignImage(CustomBaseClass):
    """model for product or service images"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_images",
                                related_query_name="product_image")
    image = models.ImageField(upload_to=image_file_path)
    image_code = models.CharField(max_length=50, default="", blank=True)
    is_main_image = models.BooleanField(default=False)

    class Meta:
        db_table = "t_product_design_image"
        ordering = ("-updated_on",)

    def __str__(self):
        """returns string representation of the model"""
        return f"{self.image.name}"
