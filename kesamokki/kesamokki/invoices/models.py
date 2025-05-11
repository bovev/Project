from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from kesamokki.reservations.models import Reservation


class InvoiceStatus(models.TextChoices):
    """Status choices for invoices."""
    PENDING = 'pending', _('Pending')
    PAID = 'paid', _('Paid')
    CANCELLED = 'cancelled', _('Cancelled')


class Invoice(models.Model):
    """
    Invoice model for tracking payments related to reservations.
    Each reservation can have only one invoice.
    """
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.PROTECT,  # Don't delete invoices if reservation is deleted
        related_name='invoice',
        verbose_name=_('Reservation')
    )
    invoice_number = models.CharField(
        _('Invoice Number'),
        max_length=20,
        unique=True,
        blank=True,  # Allow it to be blank initially, will be auto-generated
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    billed_at = models.DateField(_('Billed At'))
    due_date = models.DateField(_('Due Date'))
    amount = models.DecimalField(
        _('Amount'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True  # Will be populated from reservation total price
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.PENDING
    )
    paid_at = models.DateTimeField(_('Paid At'), null=True, blank=True)
    notes = models.TextField(_('Notes'), blank=True)

    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.reservation}"

    def save(self, *args, **kwargs):
        # Generate invoice number if not provided
        if not self.invoice_number:
            last_invoice = Invoice.objects.order_by('-id').first()
            number = 1 if not last_invoice else int(last_invoice.invoice_number.split('-')[1]) + 1
            self.invoice_number = f"INV-{number:03d}"
        
        # Set amount from reservation if not provided
        if not self.amount and self.reservation:
            self.amount = self.reservation.total_price
        
        # Check for duplicate invoices for the same reservation
        if not self.pk and Invoice.objects.filter(reservation=self.reservation).exists():
            raise ValidationError(_('An invoice already exists for this reservation.'))
        
        super().save(*args, **kwargs)
    
    def mark_as_paid(self):
        """Mark the invoice as paid and record the payment date."""
        self.status = InvoiceStatus.PAID
        self.paid_at = timezone.now()
        self.save()
        
    def is_overdue(self):
        """Check if the invoice is overdue."""
        return self.status == InvoiceStatus.PENDING and self.due_date < timezone.now().date()