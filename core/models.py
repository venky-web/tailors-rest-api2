from django.db import models


class CustomBaseClass(models.Model):
    """Base class to add created_on and updated_on fields"""
    created_on = models.DateTimeField(null=True, blank=True)
    updated_on = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True
