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
from django.core.exceptions import ValidationError

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
    template_name = 'pages/reservations_list.html'
    context_object_name = 'reservations'
    
    def get_queryset(self):
        # Show only the current user's reservations
        return Reservation.objects.filter(user=self.request.user).order_by('-created_at')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        return context
    


class ReservationDetailView(LoginRequiredMixin, DetailView):
    model = Reservation
    template_name = 'pages/reservation_details.html'
    context_object_name = 'reservation'
    
    def get_queryset(self):
        # Users can only see their own reservations
        return Reservation.objects.filter(user=self.request.user)


class CancelReservationView(LoginRequiredMixin, UpdateView):
    model = Reservation
    fields = []  # No fields needed for cancellation
    template_name = 'pages/cancel_reservation.html'
    
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
    print("==== CREATE RESERVATION AJAX ====")
    print(f"Method: {request.method}")
    print(f"Authenticated: {request.user.is_authenticated}")
    print(f"POST data: {request.POST}")
    
    if request.method == 'POST' and request.user.is_authenticated:
        cottage_id = request.POST.get('cottage_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        guests = request.POST.get('guests')
        
        print(f"Processing: cottage={cottage_id}, start={start_date}, end={end_date}, guests={guests}")
        
        # Validate all required fields are present
        if not all([cottage_id, start_date, end_date, guests]):
            error_msg = f"Missing required fields: cottage_id={cottage_id}, start_date={start_date}, end_date={end_date}, guests={guests}"
            print(f"Error: {error_msg}")
            return JsonResponse({'success': False, 'error': error_msg})
        
        try:
            cottage = Cottage.objects.get(id=cottage_id)
            start = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
            guests_count = int(guests)
            
            # Calculate total price
            nights = (end - start).days
            total_price = nights * float(cottage.base_price) + float(cottage.cleaning_fee)
            print(f"Created values: nights={nights}, total_price={total_price}")
            
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
            print(f"✅ Reservation created successfully! ID={reservation.id}")
            
            return JsonResponse({
                'success': True,
                'reservation_id': reservation.id,
                'redirect_url': reverse('reservations:detail', kwargs={'pk': reservation.id})
            })
            
        except Cottage.DoesNotExist:
            error_msg = f"Cottage with ID {cottage_id} not found"
            print(f"Error: {error_msg}")
            return JsonResponse({'success': False, 'error': error_msg})
        except ValidationError as e:
            print(f"Validation error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
        except Exception as e:
            import traceback
            print(f"Unexpected error: {str(e)}")
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
            
    error_msg = 'Invalid request or not authenticated'
    print(f"Error: {error_msg}")
    return JsonResponse({'success': False, 'error': error_msg})