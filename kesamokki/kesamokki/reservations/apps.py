from django.apps import AppConfig


class ReservationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kesamokki.reservations'
    label = 'reservations'  # the short app‐label Django will use
