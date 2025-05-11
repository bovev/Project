from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    path('', views.ReportingDashboardView.as_view(), name='dashboard'),
]