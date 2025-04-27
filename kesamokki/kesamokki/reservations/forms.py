from django import forms
from django.utils import timezone
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['cottage', 'start_date', 'end_date', 'guests']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'guests': forms.Select(attrs={'class': 'form-control'}),
            'cottage': forms.HiddenInput(),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If cottage is given, limit guests choices to cottage capacity
        if 'initial' in kwargs and 'cottage' in kwargs['initial']:
            cottage = kwargs['initial']['cottage']
            self.fields['guests'].widget = forms.Select(
                attrs={'class': 'form-control'},
                choices=[(i, f"{i} guest{'s' if i > 1 else ''}") for i in range(1, cottage.beds + 1)]
            )