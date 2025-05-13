from django.urls import path
from . import views

app_name = 'reporting'

# In urls.py
urlpatterns = [
    path('', views.ReportingDashboardView.as_view(), name='dashboard'),
    path('api/data/', views.ReportingDataAPIView.as_view(), name='api_data'),
]