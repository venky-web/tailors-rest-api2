from django.contrib import admin

from payments import models


admin.site.register(models.Payment)
