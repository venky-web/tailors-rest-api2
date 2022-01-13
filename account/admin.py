from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from account import models


class UserAdmin(BaseUserAdmin):
    """Admin class for user"""
    model = models.User
    ordering = ("-created_on",)
    list_filter = ("is_active", "user_role", "is_superuser")
    list_display = ("id", "email", "user_role", "is_active", "created_on", "updated_on")
    search_fields = ("email", "user_role", "id")
    fieldsets = (
        (None, {"fields": ("email", "password",)}),
        ("Personal info", {"fields": ("user_role",)}),
        ("Permissions", {"fields": ("is_superuser",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "user_role", "password"),
        }),
    )


# class UserProfileAdmin(Manager):
#     """Custom manager for user profiles"""
#     model = models.UserProfile
#     ordering = ("-created_on",)
#     list_filter = ("gender",)
#     list_display = ("user", "full_name", "display_name", "phone", "date_of_birth", "gender")
#     search_fields = ("full_name", "display_name", "phone")


admin.site.register(models.User, UserAdmin)
admin.site.register(models.UserProfile)
admin.site.register(models.Business)
admin.site.unregister(Group)
