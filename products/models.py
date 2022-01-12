from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
import os

from core.models import CustomBaseClass


def product_image_file_path(instance, filename):
    """returns image path"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("product-images", filename)


class Product(CustomBaseClass):
    """model for product and service"""
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(max_length=500, default="", blank=True)
    category = models.CharField(max_length=255, default="")
    units_available = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    cost = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    product_code = models.CharField(max_length=10, unique=True)
    is_service = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = "t_products"
        ordering = ("-updated_on",)

    def __str__(self):
        """returns string representation of product"""
        return f"{self.name}"

    def get_product_code(self):
        """returns product code"""
        return f"{self.product_code}"


class ProductImage(CustomBaseClass):
    """model for product or service images"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_images",
                                related_query_name="product_image")
    image = models.ImageField(upload_to=product_image_file_path)
    image_code = models.CharField(max_length=50, default="", blank=True)
    is_main_image = models.BooleanField(default=False)

    class Meta:
        db_table = "t_product_image"
        ordering = ("-updated_on",)

    def __str__(self):
        """returns string representation of the model"""
        return f"{self.image.name}"
