from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin

USER_TYPES = (
    (1, "Normal user"),
    (2, "Business user"),
    (3, "Admin"),
)

GENDERS = (
    (1, "Male"),
    (2, "Female"),
)


class BaseClass(models.Model):
    """Base class to add created_on and updated_on fields"""
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True


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
        user.is_admin = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, BaseClass, PermissionsMixin):
    """Default user model"""
    email = models.EmailField(_("Email address"), max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

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
        return self.is_admin


class UserProfile(BaseClass):
    """profile model for user object"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(_("Full name"), max_length=255, default="")
    display_name = models.CharField(_("Display name"), max_length=128, default="")
    user_type = models.CharField(_("User type"), max_length=50,
                                 choices=USER_TYPES, default=1)
    phone = models.IntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDERS, default=2)

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
