from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('', views.InvoiceListView.as_view(), name='list'),
    path('<int:pk>/', views.InvoiceDetailView.as_view(), name='detail'),
    path('create/<int:reservation_id>/', views.create_invoice_view, name='create'),
    path('<int:pk>/mark-paid/', views.mark_invoice_paid, name='mark_paid'),
    path('<int:pk>/print/', views.invoice_print_view, name='print'),
]