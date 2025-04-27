from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from kesamokki.cottages.models import Cottage
import datetime
from django.core.validators import EmailValidator, RegexValidator

class ReservationStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    CONFIRMED = 'confirmed', _('Confirmed')
    CANCELLED = 'cancelled', _('Cancelled')
    COMPLETED = 'completed', _('Completed')

class Reservation(models.Model):
    cottage = models.ForeignKey(
        Cottage, 
        on_delete=models.CASCADE, 
        related_name='reservations',
        verbose_name=_('Cottage')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name=_('User')
    )
    
    # Customer information fields
    full_name = models.CharField(_('Full Name'), max_length=100)
    email = models.EmailField(_('Email Address'), validators=[EmailValidator()])
    phone_number = models.CharField(
        _('Phone Number'), 
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9]{8,15}$',
                message=_('Enter a valid phone number. It should contain 8-15 digits and may start with a + sign.')
            )
        ]
    )
    address = models.CharField(_('Address'), max_length=255)
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    guests = models.PositiveSmallIntegerField(_('Number of Guests'))
    total_price = models.DecimalField(_('Total Price'), max_digits=10, decimal_places=2)
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=ReservationStatus.choices,
        default=ReservationStatus.PENDING
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = _('Reservation')
        verbose_name_plural = _('Reservations')
    
    def __str__(self):
        return f"{self.cottage.name} - {self.user.username} ({self.start_date} to {self.end_date})"
    
    def clean(self):
        # Check that start_date is before end_date
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError({'end_date': _('End date must be after start date.')})
        
        # Check that start_date is not in the past
        if self.start_date and self.start_date < datetime.date.today():
            raise ValidationError({'start_date': _('Reservations cannot start in the past.')})
        
        # Check for overlapping reservations for the same cottage
        overlapping = Reservation.objects.filter(
            cottage=self.cottage,
            status__in=[ReservationStatus.PENDING, ReservationStatus.CONFIRMED],
            start_date__lt=self.end_date,
            end_date__gt=self.start_date
        ).exclude(id=self.id)
        
        if overlapping.exists():
            raise ValidationError(_('The cottage is already booked for this period.'))
        
        # Check that guests don't exceed cottage capacity
        if self.guests and self.cottage and self.guests > self.cottage.beds:
            raise ValidationError({'guests': _('Number of guests exceeds cottage capacity.')})
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation before saving
        super().save(*args, **kwargs)
    
    def get_nights(self):
        """Calculate the number of nights for this reservation"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0
    
    def calculate_price(self):
        """Calculate the total price based on cottage rates and nights"""
        nights = self.get_nights()
        base_total = nights * float(self.cottage.base_price)
        cleaning_fee = float(self.cottage.cleaning_fee)
        return base_total + cleaning_fee