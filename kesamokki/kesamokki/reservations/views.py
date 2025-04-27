from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

from .models import Reservation, ReservationStatus
from kesamokki.cottages.models import Cottage
from .forms import ReservationForm

class CreateReservationView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservations/create_reservation.html'
    
    def get_initial(self):
        """Pre-fill the form with cottage info from the URL"""
        initial = super().get_initial()
        cottage_slug = self.kwargs.get('cottage_slug')
        if cottage_slug:
            cottage = get_object_or_404(Cottage, slug=cottage_slug)
            initial['cottage'] = cottage
            
            # Default to tomorrow for start_date
            tomorrow = timezone.now().date() + timezone.timedelta(days=1)
            initial['start_date'] = tomorrow
            
            # Default to tomorrow + 5 days for end_date
            initial['end_date'] = tomorrow + timezone.timedelta(days=5)
            
        return initial
    
    def form_valid(self, form):
        # Set the user to the current logged-in user
        form.instance.user = self.request.user
        
        # Calculate the total price
        cottage = form.cleaned_data['cottage']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        
        # Calculate nights
        nights = (end_date - start_date).days
        
        # Calculate total price
        form.instance.total_price = nights * cottage.base_price + cottage.cleaning_fee
        
        messages.success(self.request, 'Your reservation has been created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('reservations:detail', kwargs={'pk': self.object.pk})


class ReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'reservations/reservation_list.html'
    context_object_name = 'reservations'
    
    def get_queryset(self):
        # Show only the current user's reservations
        return Reservation.objects.filter(user=self.request.user).order_by('-created_at')


class ReservationDetailView(LoginRequiredMixin, DetailView):
    model = Reservation
    template_name = 'reservations/reservation_detail.html'
    context_object_name = 'reservation'
    
    def get_queryset(self):
        # Users can only see their own reservations
        return Reservation.objects.filter(user=self.request.user)


class CancelReservationView(LoginRequiredMixin, UpdateView):
    model = Reservation
    fields = []  # No fields needed for cancellation
    template_name = 'reservations/cancel_reservation.html'
    
    def get_queryset(self):
        # Users can only cancel their own reservations that are not already cancelled
        return Reservation.objects.filter(
            user=self.request.user,
            status__in=[ReservationStatus.PENDING, ReservationStatus.CONFIRMED]
        )
    
    def form_valid(self, form):
        reservation = self.get_object()
        reservation.status = ReservationStatus.CANCELLED
        reservation.save()
        messages.success(self.request, 'Your reservation has been cancelled.')
        return redirect('reservations:list')


# AJAX views for the cottage details page
def check_availability(request):
    """AJAX endpoint to check if a cottage is available for specific dates"""
    if request.method == 'GET':
        cottage_id = request.GET.get('cottage_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        try:
            cottage = Cottage.objects.get(id=cottage_id)
            start = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Check for overlapping reservations
            overlapping = Reservation.objects.filter(
                cottage=cottage,
                status__in=[ReservationStatus.PENDING, ReservationStatus.CONFIRMED],
                start_date__lt=end,
                end_date__gt=start
            ).exists()
            
            if overlapping:
                return JsonResponse({'available': False})
            else:
                # Calculate price
                nights = (end - start).days
                total_price = nights * float(cottage.base_price) + float(cottage.cleaning_fee)
                
                return JsonResponse({
                    'available': True, 
                    'nights': nights,
                    'base_price_total': nights * float(cottage.base_price),
                    'cleaning_fee': float(cottage.cleaning_fee),
                    'total_price': total_price
                })
                
        except (Cottage.DoesNotExist, ValueError):
            pass
            
    return JsonResponse({'available': False})


def create_reservation_ajax(request):
    """AJAX endpoint to create a reservation directly from the cottage details page"""
    if request.method == 'POST' and request.user.is_authenticated:
        cottage_id = request.POST.get('cottage_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        guests = request.POST.get('guests')
        
        try:
            cottage = Cottage.objects.get(id=cottage_id)
            start = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
            guests_count = int(guests)
            
            # Calculate total price
            nights = (end - start).days
            total_price = nights * float(cottage.base_price) + float(cottage.cleaning_fee)
            
            # Create the reservation
            reservation = Reservation(
                cottage=cottage,
                user=request.user,
                start_date=start,
                end_date=end,
                guests=guests_count,
                total_price=total_price,
                status=ReservationStatus.PENDING
            )
            
            # This will run validation via clean()
            reservation.save()
            
            return JsonResponse({
                'success': True,
                'reservation_id': reservation.id,
                'redirect_url': reverse('reservations:detail', kwargs={'pk': reservation.id})
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'Invalid request or not authenticated'})