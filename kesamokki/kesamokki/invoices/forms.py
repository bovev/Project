from django import forms
from django.utils import timezone
from datetime import timedelta

from .models import Invoice


class InvoiceForm(forms.ModelForm):
    """Form for creating and updating invoices."""
    class Meta:
        model = Invoice
        fields = ['reservation', 'billed_at', 'due_date', 'notes']
        widgets = {
            'billed_at': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'reservation': forms.HiddenInput(),  # Hide reservation field, it's pre-populated
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If this is a new invoice (no instance)
        if not kwargs.get('instance'):
            # Set default dates
            self.fields['billed_at'].initial = timezone.now().date()
            self.fields['due_date'].initial = timezone.now().date() + timedelta(days=14)