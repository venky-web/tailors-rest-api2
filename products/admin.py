from django.contrib import admin

from products import models


admin.site.register(models.Product)
admin.site.register(models.ProductImage)
