from django.urls import path
from .views import CottageListView, CottageDetailView

app_name = 'cottages'

urlpatterns = [
    path('', CottageListView.as_view(), name='list'),
    path('<slug:slug>/', CottageDetailView.as_view(), name='detail'),
]