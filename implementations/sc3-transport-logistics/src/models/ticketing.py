"""
Ticketing Models

Data models for ticketing system including bookings, tickets, and payments.
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BookingStatus(str, Enum):
    """Booking status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class PaymentStatus(str, Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class TicketStatus(str, Enum):
    """Ticket status enumeration"""
    ISSUED = "issued"
    BOARDED = "boarded"
    USED = "used"
    CANCELLED = "cancelled"


class Booking(BaseModel):
    """Booking model"""
    id: str = Field(..., description="Unique booking ID")
    customer_id: str = Field(..., description="Customer ID")
    route_id: str = Field(..., description="Route ID")
    journey_date: datetime = Field(..., description="Journey date and time")
    status: BookingStatus = Field(default=BookingStatus.PENDING)
    seats: List[str] = Field(..., description="Booked seat IDs")
    total_price: float = Field(..., description="Total booking price")
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    booking_reference: str = Field(..., description="Booking reference code")
    customer_name: str = Field(..., description="Customer name")
    customer_phone: str = Field(..., description="Customer phone")
    customer_email: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "BK-001",
                "customer_id": "CUST-001",
                "route_id": "RT-001",
                "status": "confirmed",
                "seats": ["A1", "A2"],
                "total_price": 50.00,
                "booking_reference": "BK20240130001"
            }
        }


class Ticket(BaseModel):
    """Ticket model"""
    id: str = Field(..., description="Unique ticket ID")
    booking_id: str = Field(..., description="Associated booking ID")
    seat_id: str = Field(..., description="Seat ID")
    route_id: str = Field(..., description="Route ID")
    journey_date: datetime = Field(..., description="Journey date and time")
    status: TicketStatus = Field(default=TicketStatus.ISSUED)
    ticket_number: str = Field(..., description="Ticket number")
    qr_code: str = Field(..., description="QR code data")
    passenger_name: str = Field(..., description="Passenger name")
    passenger_id: Optional[str] = None
    boarding_time: Optional[datetime] = None
    boarded_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "TK-001",
                "booking_id": "BK-001",
                "seat_id": "A1",
                "route_id": "RT-001",
                "status": "issued",
                "ticket_number": "TK20240130001",
                "passenger_name": "John Doe"
            }
        }


class Payment(BaseModel):
    """Payment model"""
    id: str = Field(..., description="Unique payment ID")
    booking_id: str = Field(..., description="Associated booking ID")
    amount: float = Field(..., description="Payment amount")
    currency: str = Field(default="USD", description="Currency code")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    payment_method: str = Field(..., description="Payment method")
    payment_gateway: str = Field(..., description="Payment gateway")
    reference_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "PAY-001",
                "booking_id": "BK-001",
                "amount": 50.00,
                "status": "completed",
                "payment_method": "card",
                "payment_gateway": "stripe"
            }
        }


class CreateBookingRequest(BaseModel):
    """Request model for creating a booking"""
    customer_id: str
    route_id: str
    journey_date: datetime
    seats: List[str]
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None


class UpdateBookingRequest(BaseModel):
    """Request model for updating a booking"""
    status: Optional[BookingStatus] = None
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    """Response model for booking operations"""
    success: bool
    message: str
    data: Optional[Booking] = None


class TicketResponse(BaseModel):
    """Response model for ticket operations"""
    success: bool
    message: str
    data: Optional[Ticket] = None


class PaymentResponse(BaseModel):
    """Response model for payment operations"""
    success: bool
    message: str
    data: Optional[Payment] = None
