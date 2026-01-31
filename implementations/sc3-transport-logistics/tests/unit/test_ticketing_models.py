"""
Unit Tests for SC-3 Ticketing Models

Tests for Booking, Ticket, and Payment models.
"""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from src.models.ticketing import (
    Booking, BookingStatus, PaymentStatus,
    Ticket, TicketStatus, Payment,
    CreateBookingRequest, UpdateBookingRequest,
    BookingResponse, TicketResponse, PaymentResponse
)


class TestBookingModel:
    """Tests for Booking model"""

    def test_create_booking(self, sample_booking):
        """Test creating a booking"""
        booking = Booking(**sample_booking)
        
        assert booking.id == "BK-001"
        assert booking.customer_id == "CUST-001"
        assert booking.route_id == "RT-001"
        assert booking.status == BookingStatus.PENDING
        assert len(booking.seats) == 2
        assert booking.total_price == 50.00

    def test_booking_status_transitions(self, sample_booking):
        """Test booking status transitions"""
        booking = Booking(**sample_booking)
        
        # Pending -> Confirmed
        booking.status = BookingStatus.CONFIRMED
        assert booking.status == BookingStatus.CONFIRMED
        
        # Confirmed -> Completed
        booking.status = BookingStatus.COMPLETED
        assert booking.status == BookingStatus.COMPLETED

    def test_booking_cancellation(self, sample_booking):
        """Test booking cancellation"""
        booking = Booking(**sample_booking)
        booking.status = BookingStatus.CANCELLED
        
        assert booking.status == BookingStatus.CANCELLED

    def test_booking_with_nigeria_phone(self, sample_booking):
        """Test booking with Nigeria phone number (INV-007)"""
        sample_booking["customer_phone"] = "+2348012345678"
        booking = Booking(**sample_booking)
        
        assert booking.customer_phone == "+2348012345678"

    def test_booking_payment_status(self, sample_booking):
        """Test booking payment status"""
        booking = Booking(**sample_booking)
        
        assert booking.payment_status == PaymentStatus.PENDING
        
        booking.payment_status = PaymentStatus.COMPLETED
        assert booking.payment_status == PaymentStatus.COMPLETED


class TestTicketModel:
    """Tests for Ticket model"""

    def test_create_ticket(self, sample_ticket):
        """Test creating a ticket"""
        ticket = Ticket(**sample_ticket)
        
        assert ticket.id == "TK-001"
        assert ticket.booking_id == "BK-001"
        assert ticket.seat_id == "SEAT-001"
        assert ticket.status == TicketStatus.ISSUED

    def test_ticket_status_transitions(self, sample_ticket):
        """Test ticket status transitions"""
        ticket = Ticket(**sample_ticket)
        
        # Issued -> Boarded
        ticket.status = TicketStatus.BOARDED
        ticket.boarded_at = datetime.utcnow()
        assert ticket.status == TicketStatus.BOARDED
        assert ticket.boarded_at is not None
        
        # Boarded -> Used
        ticket.status = TicketStatus.USED
        assert ticket.status == TicketStatus.USED

    def test_ticket_cancellation(self, sample_ticket):
        """Test ticket cancellation"""
        ticket = Ticket(**sample_ticket)
        ticket.status = TicketStatus.CANCELLED
        
        assert ticket.status == TicketStatus.CANCELLED

    def test_ticket_qr_code(self, sample_ticket):
        """Test ticket QR code"""
        ticket = Ticket(**sample_ticket)
        
        assert ticket.qr_code == "QR_DATA_TK001"

    def test_ticket_passenger_info(self, sample_ticket):
        """Test ticket passenger information"""
        sample_ticket["passenger_name"] = "Adebayo Ogundimu"
        sample_ticket["passenger_id"] = "NIG-ID-001"
        ticket = Ticket(**sample_ticket)
        
        assert ticket.passenger_name == "Adebayo Ogundimu"
        assert ticket.passenger_id == "NIG-ID-001"


class TestPaymentModel:
    """Tests for Payment model"""

    def test_create_payment(self, sample_payment):
        """Test creating a payment"""
        payment = Payment(**sample_payment)
        
        assert payment.id == "PAY-001"
        assert payment.booking_id == "BK-001"
        assert payment.amount == 50.00
        assert payment.status == PaymentStatus.PENDING

    def test_payment_completion(self, sample_payment):
        """Test payment completion"""
        payment = Payment(**sample_payment)
        
        payment.status = PaymentStatus.COMPLETED
        payment.completed_at = datetime.utcnow()
        payment.reference_id = "REF-12345"
        
        assert payment.status == PaymentStatus.COMPLETED
        assert payment.completed_at is not None
        assert payment.reference_id == "REF-12345"

    def test_payment_failure(self, sample_payment):
        """Test payment failure"""
        payment = Payment(**sample_payment)
        
        payment.status = PaymentStatus.FAILED
        payment.error_message = "Insufficient funds"
        
        assert payment.status == PaymentStatus.FAILED
        assert payment.error_message == "Insufficient funds"

    def test_payment_refund(self, sample_payment):
        """Test payment refund"""
        payment = Payment(**sample_payment)
        payment.status = PaymentStatus.COMPLETED
        
        payment.status = PaymentStatus.REFUNDED
        assert payment.status == PaymentStatus.REFUNDED

    def test_payment_with_ngn_currency(self, sample_payment):
        """Test payment with Nigerian Naira (INV-007)"""
        sample_payment["currency"] = "NGN"
        sample_payment["amount"] = 15000.00
        payment = Payment(**sample_payment)
        
        assert payment.currency == "NGN"
        assert payment.amount == 15000.00

    def test_payment_with_paystack(self, sample_payment):
        """Test payment with Paystack gateway (popular in Nigeria)"""
        sample_payment["payment_gateway"] = "paystack"
        sample_payment["payment_method"] = "card"
        payment = Payment(**sample_payment)
        
        assert payment.payment_gateway == "paystack"
        assert payment.payment_method == "card"


class TestCreateBookingRequest:
    """Tests for CreateBookingRequest model"""

    def test_create_booking_request(self):
        """Test creating a booking request"""
        request = CreateBookingRequest(
            customer_id="CUST-001",
            route_id="RT-001",
            journey_date=datetime.utcnow() + timedelta(days=1),
            seats=["A1", "A2"],
            customer_name="John Doe",
            customer_phone="+2348012345678",
            customer_email="john@example.com"
        )
        
        assert request.customer_id == "CUST-001"
        assert len(request.seats) == 2

    def test_create_booking_request_without_email(self):
        """Test creating a booking request without email"""
        request = CreateBookingRequest(
            customer_id="CUST-001",
            route_id="RT-001",
            journey_date=datetime.utcnow() + timedelta(days=1),
            seats=["A1"],
            customer_name="John Doe",
            customer_phone="+2348012345678"
        )
        
        assert request.customer_email is None


class TestUpdateBookingRequest:
    """Tests for UpdateBookingRequest model"""

    def test_update_booking_status(self):
        """Test updating booking status"""
        request = UpdateBookingRequest(
            status=BookingStatus.CONFIRMED
        )
        
        assert request.status == BookingStatus.CONFIRMED

    def test_update_booking_notes(self):
        """Test updating booking notes"""
        request = UpdateBookingRequest(
            notes="Customer requested window seat"
        )
        
        assert request.notes == "Customer requested window seat"


class TestResponseModels:
    """Tests for response models"""

    def test_booking_response_success(self, sample_booking):
        """Test successful booking response"""
        booking = Booking(**sample_booking)
        response = BookingResponse(
            success=True,
            message="Booking created successfully",
            data=booking
        )
        
        assert response.success is True
        assert response.data.id == "BK-001"

    def test_booking_response_failure(self):
        """Test failed booking response"""
        response = BookingResponse(
            success=False,
            message="Booking failed: No seats available",
            data=None
        )
        
        assert response.success is False
        assert response.data is None

    def test_ticket_response(self, sample_ticket):
        """Test ticket response"""
        ticket = Ticket(**sample_ticket)
        response = TicketResponse(
            success=True,
            message="Ticket issued successfully",
            data=ticket
        )
        
        assert response.success is True
        assert response.data.ticket_number == "TK20240130001"

    def test_payment_response(self, sample_payment):
        """Test payment response"""
        payment = Payment(**sample_payment)
        response = PaymentResponse(
            success=True,
            message="Payment processed successfully",
            data=payment
        )
        
        assert response.success is True
        assert response.data.amount == 50.00
