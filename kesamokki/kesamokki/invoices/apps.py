from django.apps import AppConfig


class InvoicesConfig(AppConfig):
    name = "kesamokki.invoices"
    label = "invoices"               # the short app‐label Django will use
    default_auto_field = "django.db.models.BigAutoField"
