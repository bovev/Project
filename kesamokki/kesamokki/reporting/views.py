from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta, date
import calendar
import json
from django.http import JsonResponse
from django.views import View
from kesamokki.invoices.models import Invoice
from kesamokki.reservations.models import Reservation
from kesamokki.cottages.models import Cottage


class StaffRequiredMixin(UserPassesTestMixin):
    """Verify that the current user is staff."""
    def test_func(self):
        return self.request.user.is_staff


class ReportingDashboardView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    """Dashboard with consolidated revenue and occupancy reporting."""
    template_name = 'pages/reporting.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Reporting Dashboard'
        
        # Default to showing the last 12 months
        end_date = timezone.now().date().replace(day=1)
        start_date = (end_date - timedelta(days=365)).replace(day=1)
        
        # Parse filter parameters from request
        filter_start = self.request.GET.get('start')
        filter_end = self.request.GET.get('end')
        filter_status = self.request.GET.get('status', 'all')
        filter_cottage = self.request.GET.get('cottage', 'all')
        
        try:
            if filter_start:
                start_date = date.fromisoformat(filter_start)
            if filter_end:
                # Set to first day of the month
                end_date = date.fromisoformat(filter_end).replace(day=1)
                # Add a month to include the entire month in the filter
                end_date = (end_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        except ValueError:
            # If date parsing fails, use defaults
            pass
        
        # ====== REVENUE DATA ======
        # Base query for invoices
        invoice_query = Invoice.objects.filter(
            billed_at__gte=start_date,
            billed_at__lt=end_date
        )
        
        # Apply status filter if specified
        if filter_status != 'all':
            invoice_query = invoice_query.filter(status=filter_status)
        
        # Group invoices by month and sum amounts
        monthly_revenue = invoice_query.annotate(
            month=TruncMonth('billed_at')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        # For chart data
        months = []
        revenue_data = []
        
        # Get all months in the range for consistency
        current = start_date
        month_list = []
        while current < end_date:
            month_name = current.strftime('%B %Y')
            month_list.append({
                'date': current,
                'name': month_name,
                'year': current.year,
                'month': current.month
            })
            current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        # Fill in revenue data with 0 for months with no data
        revenue_by_month = {item['month'].strftime('%B %Y'): float(item['total']) for item in monthly_revenue}
        
        for month in month_list:
            months.append(month['name'])
            revenue_data.append(revenue_by_month.get(month['name'], 0))
            
        context['months_json'] = json.dumps(months)
        context['revenue_data'] = json.dumps(revenue_data)
        context['total_revenue'] = sum(revenue_data)
        
        # ====== OCCUPANCY DATA ======
        # Get all cottages for filtering
        cottages = Cottage.objects.all()
        context['cottages'] = cottages
        
        # Initialize occupancy data structure
        cottage_occupancy = []
        
        # Process each cottage
        for cottage in cottages:
            # Skip if filtering by cottage and this isn't it
            if filter_cottage != 'all' and str(cottage.id) != filter_cottage:
                continue
            
            occupancy_data = []
            
            for month_info in month_list:
                month = month_info['month']
                year = month_info['year']
                
                # Get days in this month
                days_in_month = calendar.monthrange(year, month)[1]
                first_day = date(year, month, 1)
                last_day = date(year, month, days_in_month)
                
                # Query reservations in this month for this cottage
                reservations = Reservation.objects.filter(
                    cottage=cottage,
                    start_date__lte=last_day,
                    end_date__gte=first_day,
                )
                
                # Calculate occupied days
                occupied_days = 0
                for res in reservations:
                    # Adjust dates to be within the month
                    res_start = max(res.start_date, first_day)
                    res_end = min(res.end_date, last_day)
                    occupied_days += (res_end - res_start).days + 1
                
                # Cap at days in the month (in case of overlaps)
                occupied_days = min(occupied_days, days_in_month)
                
                # Calculate occupancy rate
                occupancy_rate = round((occupied_days / days_in_month) * 100, 1)
                occupancy_data.append(occupancy_rate)
            
            cottage_occupancy.append({
                'name': cottage.name,
                'data': occupancy_data,
                'color': self._get_random_color(cottage.id)  # Generate consistent color based on cottage ID
            })
        
        context['cottage_occupancy'] = json.dumps(cottage_occupancy)
        
        # Pass filter values
        context['filter_start'] = start_date.isoformat()
        context['filter_end'] = (end_date - timedelta(days=1)).isoformat()  # End of previous month
        context['filter_status'] = filter_status
        context['filter_cottage'] = filter_cottage
        
        return context
    
    def _get_random_color(self, seed):
        """Generate a consistent color based on a seed value."""
        import hashlib
        
        # Create a hash from the seed
        hash_obj = hashlib.md5(str(seed).encode())
        hash_hex = hash_obj.hexdigest()
        
        # Use portions of the hash for R, G, B
        r = int(hash_hex[0:2], 16) % 200 + 25  # 25-224 range
        g = int(hash_hex[2:4], 16) % 200 + 25
        b = int(hash_hex[4:6], 16) % 200 + 25
        
        return f'rgb({r}, {g}, {b})'


class ReportingDataAPIView(LoginRequiredMixin, StaffRequiredMixin, View):
    """API endpoint to get reporting data as JSON."""
    
    def get(self, request):
        # Default to showing the last 12 months
        end_date = timezone.now().date().replace(day=1)
        start_date = (end_date - timedelta(days=365)).replace(day=1)
        
        # Parse filter parameters from request
        filter_start = request.GET.get('start')
        filter_end = request.GET.get('end')
        filter_status = request.GET.get('status', 'all')
        filter_cottage = request.GET.get('cottage', 'all')
        
        try:
            if filter_start:
                start_date = date.fromisoformat(filter_start)
            if filter_end:
                # Set to first day of the month
                end_date = date.fromisoformat(filter_end).replace(day=1)
                # Add a month to include the entire month in the filter
                end_date = (end_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        except ValueError:
            # If date parsing fails, use defaults
            pass
            
        # ====== REVENUE DATA ======
        # Base query for invoices
        invoice_query = Invoice.objects.filter(
            billed_at__gte=start_date,
            billed_at__lt=end_date
        )
        
        # Apply status filter if specified
        if filter_status != 'all':
            invoice_query = invoice_query.filter(status=filter_status)
        
        # Group invoices by month and sum amounts
        monthly_revenue = invoice_query.annotate(
            month=TruncMonth('billed_at')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        # For chart data
        months = []
        revenue_data = []
        
        # Get all months in the range for consistency
        current = start_date
        month_list = []
        while current < end_date:
            month_name = current.strftime('%B %Y')
            month_list.append({
                'date': current,
                'name': month_name,
                'year': current.year,
                'month': current.month
            })
            current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        # Fill in revenue data with 0 for months with no data
        revenue_by_month = {item['month'].strftime('%B %Y'): float(item['total']) for item in monthly_revenue}
        
        for month in month_list:
            months.append(month['name'])
            revenue_data.append(revenue_by_month.get(month['name'], 0))
        
        # ====== OCCUPANCY DATA ======
        # Get all cottages for filtering
        cottages = Cottage.objects.all()
        
        # Initialize occupancy data structure
        cottage_occupancy = []
        
        # Process each cottage
        for cottage in cottages:
            # Skip if filtering by cottage and this isn't it
            if filter_cottage != 'all' and str(cottage.id) != filter_cottage:
                continue
            
            occupancy_data = []
            
            for month_info in month_list:
                month = month_info['month']
                year = month_info['year']
                
                # Get days in this month
                days_in_month = calendar.monthrange(year, month)[1]
                first_day = date(year, month, 1)
                last_day = date(year, month, days_in_month)
                
                # Query reservations in this month for this cottage
                reservations = Reservation.objects.filter(
                    cottage=cottage,
                    start_date__lte=last_day,
                    end_date__gte=first_day,
                )
                
                # Calculate occupied days
                occupied_days = 0
                for res in reservations:
                    # Adjust dates to be within the month
                    res_start = max(res.start_date, first_day)
                    res_end = min(res.end_date, last_day)
                    occupied_days += (res_end - res_start).days + 1
                
                # Cap at days in the month (in case of overlaps)
                occupied_days = min(occupied_days, days_in_month)
                
                # Calculate occupancy rate
                occupancy_rate = round((occupied_days / days_in_month) * 100, 1)
                occupancy_data.append(occupancy_rate)
            
            cottage_occupancy.append({
                'name': cottage.name,
                'data': occupancy_data,
                'color': self._get_random_color(cottage.id)  # Generate consistent color based on cottage ID
            })

        # Calculate total revenue for stats
        total_revenue = sum(revenue_data)
        
        return JsonResponse({
            'months': months,
            'revenue': revenue_data,
            'occupancy': cottage_occupancy,
            'stats': {
                'total_revenue': total_revenue
            },
            'translations': {
                'monthlyRevenue': 'Monthly Revenue (€)',
                'revenue': 'Revenue'
            }
        })
    def _get_random_color(self, seed):
        """Generate a consistent color based on a seed value."""
        import hashlib
        
        # Create a hash from the seed
        hash_obj = hashlib.md5(str(seed).encode())
        hash_hex = hash_obj.hexdigest()
        
        # Use portions of the hash for R, G, B
        r = int(hash_hex[0:2], 16) % 200 + 25  # 25-224 range
        g = int(hash_hex[2:4], 16) % 200 + 25
        b = int(hash_hex[4:6], 16) % 200 + 25
        
        return f'rgb({r}, {g}, {b})'

        
