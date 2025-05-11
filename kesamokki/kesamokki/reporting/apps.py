from django.apps import AppConfig


class ReportingConfig(AppConfig):
    name = "kesamokki.reporting"
    label = "reporting"               # the short app‐label Django will use
    default_auto_field = "django.db.models.BigAutoField"
