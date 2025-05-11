from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta

from .models import Invoice
from .forms import InvoiceForm
from kesamokki.reservations.models import Reservation


class InvoiceListView(LoginRequiredMixin, ListView):
    """View for listing all invoices."""
    model = Invoice
    template_name = 'pages/invoice_list.html'  # Using the pages folder convention
    context_object_name = 'invoices'
    paginate_by = 20  # Show 20 invoices per page
    
    def get_queryset(self):
        """Filter invoices by user if not staff and apply status filters."""
        queryset = Invoice.objects.all() if self.request.user.is_staff else Invoice.objects.filter(reservation__user=self.request.user)
        
        # Filter by status if provided in GET parameters
        status_filter = self.request.GET.get('status')
        if status_filter in ['pending', 'paid', 'cancelled']:
            queryset = queryset.filter(status=status_filter)
        
        # Filter overdue invoices if requested
        if status_filter == 'overdue':
            queryset = queryset.filter(
                status='pending',
                due_date__lt=timezone.now().date()
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_queryset = Invoice.objects.all() if self.request.user.is_staff else Invoice.objects.filter(reservation__user=self.request.user)
        
        # Add counts for different statuses
        context['pending_count'] = base_queryset.filter(status='pending').count()
        context['paid_count'] = base_queryset.filter(status='paid').count()
        context['cancelled_count'] = base_queryset.filter(status='cancelled').count()
        
        # Count overdue invoices
        context['overdue_count'] = base_queryset.filter(
            status='pending',
            due_date__lt=timezone.now().date()
        ).count()
        
        # Get current filter
        context['current_status'] = self.request.GET.get('status', 'all')
        
        return context


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    """View for displaying a single invoice."""
    model = Invoice
    template_name = 'pages/invoice_detail.html'
    context_object_name = 'invoice'
    
    def get_queryset(self):
        """Ensure user can only view their own invoices unless staff."""
        if self.request.user.is_staff:
            return Invoice.objects.all()
        return Invoice.objects.filter(reservation__user=self.request.user)


@login_required
def create_invoice_view(request, reservation_id):
    """View for creating a new invoice from a reservation."""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Check if user is authorized to create invoice for this reservation
    if not request.user.is_staff and reservation.user != request.user:
        messages.error(request, "You don't have permission to create an invoice for this reservation.")
        return redirect('reservations:list')
    
    # Check if invoice already exists
    if hasattr(reservation, 'invoice'):
        messages.warning(request, "An invoice already exists for this reservation.")
        return redirect('invoices:detail', pk=reservation.invoice.pk)
    
    # Initial form data
    initial_data = {
        'reservation': reservation,
        'billed_at': timezone.now().date(),
        'due_date': timezone.now().date() + timedelta(days=14),  # Default due date: 14 days
        'amount': reservation.total_price,
    }
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, "Invoice created successfully!")
            return redirect('invoices:detail', pk=invoice.pk)
    else:
        form = InvoiceForm(initial=initial_data)
    
    return render(request, 'pages/create_invoice.html', {
        'form': form,
        'reservation': reservation,
    })


@login_required
def mark_invoice_paid(request, pk):
    """Mark an invoice as paid."""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Check if user is authorized
    if not request.user.is_staff and invoice.reservation.user != request.user:
        messages.error(request, "You don't have permission to update this invoice.")
        return redirect('invoices:list')
    
    if request.method == 'POST':
        invoice.mark_as_paid()
        messages.success(request, "Invoice marked as paid successfully!")
    
    return redirect('invoices:detail', pk=invoice.pk)

@login_required
def invoice_print_view(request, pk):
    """Display a print-friendly version of the invoice."""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Check if user is authorized to view this invoice
    if not request.user.is_staff and invoice.reservation.user != request.user:
        messages.error(request, "You don't have permission to access this invoice.")
        return redirect('invoices:list')
    
    return render(request, 'pages/invoice_print.html', {
        'invoice': invoice
    })