from django.views.generic import ListView, DetailView
from django.shortcuts import render
from .models import Cottage, CottageImage
from django.contrib.auth.mixins import LoginRequiredMixin



class CottageListView(ListView):
    model = Cottage
    template_name = 'pages/cottage-browsing.html'
    context_object_name = 'cottages'
    
    def get_queryset(self):
        # Start with active cottages
        queryset = Cottage.objects.filter(active=True).prefetch_related('images')
        
        # Apply filters from request.GET
        location = self.request.GET.get('location', '')
        min_beds = self.request.GET.get('min_beds', '')
        max_price = self.request.GET.get('max_price', '')
        
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        if min_beds and min_beds.isdigit():
            queryset = queryset.filter(beds__gte=int(min_beds))
        
        if max_price and max_price.isdigit():
            queryset = queryset.filter(base_price__lte=int(max_price))
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CottageDetailView(LoginRequiredMixin, DetailView):
    model = Cottage
    template_name = 'cottages/cottage_detail.html'
    context_object_name = 'cottage'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context you need
        return context