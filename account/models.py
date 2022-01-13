from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.conf import settings

from core.models import CustomBaseClass

USER_TYPES = (
    ("normal_user", "Normal user"),
    ("business_user", "Business user"),
    ("business_staff", "Business staff"),
    ("admin", "Admin"),
)

GENDERS = (
    ("male", "Male"),
    ("female", "Female"),
    ("other", "Other"),
)

class UserManager(BaseUserManager):
    """Default manager for user objects"""

    def create_user(self, email, password=None, **extra_fields):
        """creates a new user in the DB"""
        if not email or not password:
            return ValueError(_("Email or password is missing"))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        """creates an admin user in the db"""
        user = self.create_user(email, password, **extra_fields)
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, CustomBaseClass, PermissionsMixin):
    """Default user model"""
    email = models.EmailField(_("Email address"), max_length=255, unique=True)
    user_role = models.CharField(_("User role"), max_length=50,
                                 choices=USER_TYPES, default="normal_user")
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "t_user"
        ordering = ("-created_on",)

    def __str__(self):
        """returns string representation of user"""
        return f"{self.email}"

    def has_perm(self, perm, obj=None):
        """returns True if a user has permission"""
        return True

    def has_module_perm(self, app_label):
        """returns True if a user has permission to the module"""
        return True

    @property
    def is_staff(self):
        """returns True if user is admin or staff member"""
        return self.is_superuser


class UserProfile(CustomBaseClass):
    """profile model for user object"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,
                                related_name="profile")
    full_name = models.CharField(_("Full name"), max_length=255, default="")
    display_name = models.CharField(_("Display name"), max_length=128, default="")
    phone = models.IntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDERS, default="female")

    class Meta:
        db_table = "t_user_profile"
        ordering = ("-created_on",)

    def __str__(self):
        """returns string representation of user profile"""
        full_name = self.get_full_name()
        short_name = self.get_short_name()
        if full_name:
            return f"{full_name}"
        elif short_name:
            return f"{short_name}"
        else:
            return f"{self.phone}"

    def get_full_name(self):
        """returns full name of user"""
        return f"{self.full_name}"

    def get_short_name(self):
        """returns display name of the user"""
        return f"{self.display_name}"


class Business(CustomBaseClass):
    """model for businesses"""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                              null=True, related_name="business")
    name = models.CharField(max_length=255, unique=True)
    max_staff_count = models.IntegerField(default=2)

    class Meta:
        db_table = "t_business"
        ordering = ("-created_on",)
        verbose_name_plural = "businesses"

    def __str__(self):
        """returns string representation of business"""
        return f"{self.name}"
