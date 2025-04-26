from django.shortcuts import render
from django.views.generic import TemplateView
from kesamokki.cottages.models import Cottage

# Create your views here.

class HomePageView(TemplateView):
    template_name = "pages/home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the three most recently added active cottages
        context['featured_cottages'] = Cottage.objects.filter(active=True).prefetch_related('images')[:3]
        return context