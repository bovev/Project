from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('', views.ReservationListView.as_view(), name='list'),
    path('<int:pk>/', views.ReservationDetailView.as_view(), name='detail'),
    path('create/<slug:cottage_slug>/', views.CreateReservationView.as_view(), name='create'),
    path('<int:pk>/cancel/', views.CancelReservationView.as_view(), name='cancel'),
    path('check-availability/', views.check_availability, name='check-availability'),
    path('create-ajax/', views.create_reservation_ajax, name='create-ajax'),
]