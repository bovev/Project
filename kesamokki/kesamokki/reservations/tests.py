from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime
import json
from decimal import Decimal
from django.core.exceptions import ValidationError

from kesamokki.cottages.models import Cottage
from .models import Reservation, ReservationStatus
from kesamokki.users.models import Customer

User = get_user_model()

class ReservationModelTests(TestCase):
    """Tests for the Reservation model"""
    
    def setUp(self):
        # Create a user with only the fields your custom user model supports
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123'
        )
        
        # Create a customer associated with the user
        self.customer = Customer.objects.create(
            user=self.user,
            full_name='Test User',
            phone='+358401234567',
            address_line1='Test Address 123'
        )
        
        # Create a cottage
        self.cottage = Cottage.objects.create(
            name='Test Cottage',
            slug='test-cottage',
            description='A test cottage',
            location='Test Location',
            beds=4,
            base_price=Decimal('100.00'),
            cleaning_fee=Decimal('50.00')
        )
        
        # Set up dates for testing
        today = timezone.now().date()
        self.tomorrow = today + datetime.timedelta(days=1)
        self.day_after = today + datetime.timedelta(days=2)
        self.next_week = today + datetime.timedelta(days=7)
        
    def test_create_valid_reservation(self):
        """Test creating a valid reservation"""
        reservation = Reservation.objects.create(
            cottage=self.cottage,
            user=self.user,
            customer=self.customer,  # Add customer reference
            start_date=self.tomorrow,
            end_date=self.next_week,
            guests=2,
            total_price=Decimal('650.00'),  # 6 nights * 100 + 50 cleaning fee
            status=ReservationStatus.PENDING
        )
        
        self.assertEqual(reservation.cottage, self.cottage)
        self.assertEqual(reservation.user, self.user)
        self.assertEqual(reservation.customer, self.customer)  # Test customer association
        self.assertEqual(reservation.guests, 2)
        self.assertEqual(reservation.status, ReservationStatus.PENDING)
        self.assertEqual(reservation.get_nights(), 6)
        
        
    def test_reservation_string_representation(self):
        """Test the string representation of a reservation"""
        reservation = Reservation.objects.create(
            cottage=self.cottage,
            user=self.user,
            customer=self.customer,  # Add customer reference
            start_date=self.tomorrow,
            end_date=self.next_week,
            guests=2,
            total_price=Decimal('650.00'),
            status=ReservationStatus.PENDING
        )
        
        # Update expected string format if needed
        expected_str = f"{self.cottage.name} - {self.user.username} ({self.tomorrow} to {self.next_week})"
        self.assertEqual(str(reservation), expected_str)
        
    def test_end_date_before_start_date(self):
        """Test validation error when end date is before start date"""
        with self.assertRaises(ValidationError):
            reservation = Reservation(
                cottage=self.cottage,
                user=self.user,
                customer=self.customer,  # Add customer reference
                start_date=self.next_week,
                end_date=self.tomorrow,  # End date before start date
                guests=2,
                total_price=Decimal('650.00'),
                status=ReservationStatus.PENDING
            )
            reservation.save()
            
    def test_start_date_in_past(self):
        """Test validation error when start date is in the past"""
        yesterday = timezone.now().date() - datetime.timedelta(days=1)
        
        with self.assertRaises(ValidationError):
            reservation = Reservation(
                cottage=self.cottage,
                user=self.user,
                customer=self.customer,  # Add customer reference
                start_date=yesterday,  # Start date in the past
                end_date=self.next_week,
                guests=2,
                total_price=Decimal('650.00'),
                status=ReservationStatus.PENDING
            )
            reservation.save()
            
    def test_overlapping_reservations(self):
        """Test validation error for overlapping reservations"""
        # Create first reservation
        Reservation.objects.create(
            cottage=self.cottage,
            user=self.user,
            customer=self.customer,  # Add customer reference
            start_date=self.tomorrow,
            end_date=self.next_week,
            guests=2,
            total_price=Decimal('650.00'),
            status=ReservationStatus.CONFIRMED
        )
        
        # Create another customer for second reservation, left out user since it is not mandatory
        another_customer = Customer.objects.create(
            full_name='Another User',
            phone='+358407654321',
            address_line1='Another Address 456'
        )
        
        # Try to create overlapping reservation
        with self.assertRaises(ValidationError):
            overlap_res = Reservation(
                cottage=self.cottage,
                user=self.user,
                customer=another_customer,  # Use second customer
                start_date=self.day_after,  # Overlaps with first reservation
                end_date=self.next_week,
                guests=2,
                total_price=Decimal('550.00'),
                status=ReservationStatus.PENDING
            )
            overlap_res.save()
            