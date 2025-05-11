
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField, BooleanField, DateTimeField, OneToOneField, CASCADE
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for kesamokki.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})
    
    
class Customer(models.Model):
    """Core customer / guest profile."""

    user = OneToOneField(
        User,
        related_name="customer",
        on_delete=CASCADE,
        help_text="Link to auth user",
        null=True,
        blank=True,
    )
    full_name = CharField(max_length=120)
    phone = CharField(max_length=30, blank=True)
    email = EmailField(max_length=120, blank=True)
    address_line1 = CharField(_("Address line 1"), max_length=120)
    address_line2 = CharField(_("Address line 2"), max_length=120, blank=True)
    postal_code = CharField(max_length=20)
    city = CharField(max_length=60)
    country_code = CharField(max_length=2, default="FI")

    gdpr_consent = BooleanField(default=False)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name
