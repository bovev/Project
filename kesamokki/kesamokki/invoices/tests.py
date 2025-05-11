from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.urls import reverse
from datetime import timedelta, date

from kesamokki.users.models import User, Customer
from kesamokki.cottages.models import Cottage
from kesamokki.reservations.models import Reservation, ReservationStatus
from .models import Invoice

class InvoiceModelTests(TestCase):
    """Test suite for the Invoice model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )
        
        # Create a customer
        self.customer = Customer.objects.create(
            full_name='Test Customer',
            email='customer@example.com',
            address_line1='123 Test St',
            postal_code='00100',
            city='Helsinki',
            country_code='FI',
            gdpr_consent=True
        )
        
        # Create a cottage - Fix field names to match model
        self.cottage = Cottage.objects.create(
            name='Test Cottage',
            description='A test cottage',
            location='Helsinki, Finland',  # Use location instead of separate address and city
            beds=4,
            base_price=100.00,
            cleaning_fee=50.00
        )
        
        # Create a reservation
        today = timezone.now().date()
        self.reservation = Reservation.objects.create(
            cottage=self.cottage,
            user=self.user,
            customer=self.customer,
            start_date=today + timedelta(days=1),
            end_date=today + timedelta(days=3),
            guests=2,
            total_price=250.00,
            status=ReservationStatus.CONFIRMED
        )
    
    def test_create_invoice(self):
        """Test creating an invoice."""
        invoice = Invoice.objects.create(
            reservation=self.reservation,
            billed_at=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=14),
            invoice_number='INV-001'
        )
        self.assertIsNotNone(invoice.id)
        self.assertEqual(invoice.reservation, self.reservation)
        self.assertEqual(invoice.amount, self.reservation.total_price)
        self.assertEqual(invoice.status, 'pending')
    
    def test_invoice_str_method(self):
        """Test the string representation of an Invoice."""
        invoice = Invoice.objects.create(
            reservation=self.reservation,
            billed_at=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=14),
            invoice_number='INV-001'
        )
        # Update expected string format to match your __str__ implementation
        expected_str = f"Invoice {invoice.invoice_number} for {self.reservation}"
        self.assertEqual(str(invoice), expected_str)
    
    def test_auto_invoice_number(self):
        """Test auto-generation of invoice number if not provided."""
        invoice = Invoice.objects.create(
            reservation=self.reservation,
            billed_at=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=14)
        )
        self.assertIsNotNone(invoice.invoice_number)
        self.assertTrue(invoice.invoice_number.startswith('INV-'))
    
    def test_invoice_amount_auto_from_reservation(self):
        """Test that invoice amount is automatically set from reservation."""
        invoice = Invoice.objects.create(
            reservation=self.reservation,
            billed_at=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=14)
        )
        self.assertEqual(invoice.amount, self.reservation.total_price)
    
    def test_mark_as_paid(self):
        """Test marking an invoice as paid."""
        invoice = Invoice.objects.create(
            reservation=self.reservation,
            billed_at=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=14)
        )
        self.assertEqual(invoice.status, 'pending')
        invoice.mark_as_paid()
        self.assertEqual(invoice.status, 'paid')
        self.assertIsNotNone(invoice.paid_at)
    
    def test_validation_error_on_duplicate_invoice(self):
        """Test that a validation error is raised if invoice exists for reservation."""
        Invoice.objects.create(
            reservation=self.reservation,
            billed_at=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=14)
        )
        with self.assertRaises(ValidationError):
            Invoice.objects.create(
                reservation=self.reservation,
                billed_at=timezone.now().date(),
                due_date=timezone.now().date() + timedelta(days=14)
            )


class InvoiceViewTests(TestCase):
    """Test suite for the Invoice views."""
    
    def setUp(self):
        """Set up test data."""
        # Create a user and log them in
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )
        self.client.login(email='test@example.com', password='testpass123')
        
        # Create a customer
        self.customer = Customer.objects.create(
            full_name='Test Customer',
            email='customer@example.com',
            address_line1='123 Test St',
            postal_code='00100',
            city='Helsinki',
            country_code='FI',
            gdpr_consent=True
        )
        
        # Create a cottage - Fix field names to match model
        self.cottage = Cottage.objects.create(
            name='Test Cottage',
            description='A test cottage',
            location='Helsinki, Finland',  # Use location instead of separate address and city
            beds=4,
            base_price=100.00,
            cleaning_fee=50.00
        )
        
        # Create a reservation
        today = timezone.now().date()
        self.reservation = Reservation.objects.create(
            cottage=self.cottage,
            user=self.user,
            customer=self.customer,
            start_date=today + timedelta(days=1),
            end_date=today + timedelta(days=3),
            guests=2,
            total_price=250.00,
            status=ReservationStatus.CONFIRMED
        )
        
        # Create an invoice
        self.invoice = Invoice.objects.create(
            reservation=self.reservation,
            billed_at=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=14),
            invoice_number='INV-001'
        )
    
    def test_invoice_list_view(self):
        """Test accessing the invoice list view."""
        response = self.client.get(reverse('invoices:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'INV-001')
    
    def test_invoice_detail_view(self):
        """Test accessing the invoice detail view."""
        response = self.client.get(
            reverse('invoices:detail', kwargs={'pk': self.invoice.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'INV-001')
        self.assertContains(response, str(self.reservation.total_price))
