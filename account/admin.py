from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from account import models


class UserAdmin(BaseUserAdmin):
    """Admin class for user"""
    model = models.User
    ordering = ("-created_on",)
    list_filter = ("is_active", "user_role", "is_superuser")
    list_display = ("id", "username", "email", "user_role", "is_active",
                    "business", "created_on", "updated_on")
    search_fields = ("username", "email", "user_role", "id")
    fieldsets = (
        (None, {"fields": ("username", "email", "password",)}),
        ("Personal info", {"fields": ("user_role",)}),
        ("Permissions", {"fields": ("is_superuser",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "user_role", "password"),
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.UserProfile)
admin.site.register(models.UserBusinessRelation)
admin.site.register(models.Business)
admin.site.unregister(Group)
