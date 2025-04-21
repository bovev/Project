from django.views.generic import ListView, DetailView
from django.shortcuts import render
from .models import Cottage, CottageImage
from django.contrib.auth.mixins import LoginRequiredMixin



class CottageListView(ListView):
    model = Cottage
    template_name = 'cottages/cottage_list.html'
    context_object_name = 'cottages'
    
    def get_queryset(self):
        # Return only active cottages
        return Cottage.objects.filter(active=True).prefetch_related('images')
    
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