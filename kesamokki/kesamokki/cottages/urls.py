from django.urls import path
from . import views

app_name = 'cottages'

urlpatterns = [
    path('', views.CottageListView.as_view(), name='list'),
    path('<slug:slug>/', views.CottageDetailView.as_view(), name='detail'),
]