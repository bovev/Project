from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User, Customer

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("name",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["email", "name", "is_superuser"]
    search_fields = ["name", "email"]
    ordering = ["id"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "get_email",
        "phone",
        "city",
        "country_code",
        "gdpr_consent",
    )
    list_filter = ("country_code", "gdpr_consent")
    search_fields = ("full_name", "user__email", "email", "phone", "city")
    
    fieldsets = (
        (None, {
            "fields": ("user", "full_name", "email", "phone"),
        }),
        ("Address Information", {
            "fields": ("address_line1", "address_line2", "postal_code", "city", "country_code"),
        }),
        ("Settings", {
            "fields": ("gdpr_consent",),
        }),
    )
    
    def get_email(self, obj):
        """Get email from the related user model or the customer model."""
        if obj.user:
            return obj.user.email
        return obj.email or "-"
    
    get_email.short_description = "Email"
    
    def save_model(self, request, obj, form, change):
        """Override save method to handle email synchronization."""
        # If user is selected, copying user email to customer email
        if obj.user and not obj.email:
            obj.email = obj.user.email
        super().save_model(request, obj, form, change)