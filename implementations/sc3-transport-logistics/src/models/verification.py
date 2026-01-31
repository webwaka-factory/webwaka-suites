"""
Verification Models

Data models for ticket verification and boarding passes.
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class VerificationStatus(str, Enum):
    """Verification status enumeration"""
    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    ALREADY_USED = "already_used"
    NOT_FOUND = "not_found"


class BoardingPassStatus(str, Enum):
    """Boarding pass status enumeration"""
    ISSUED = "issued"
    USED = "used"
    CANCELLED = "cancelled"


class TicketVerification(BaseModel):
    """Ticket verification model"""
    id: str = Field(..., description="Unique verification ID")
    ticket_id: str = Field(..., description="Ticket ID")
    qr_code: str = Field(..., description="QR code data")
    status: VerificationStatus = Field(default=VerificationStatus.VALID)
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    verification_location: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "VER-001",
                "ticket_id": "TK-001",
                "qr_code": "QR_DATA_HERE",
                "status": "valid"
            }
        }


class BoardingPass(BaseModel):
    """Boarding pass model"""
    id: str = Field(..., description="Unique boarding pass ID")
    ticket_id: str = Field(..., description="Ticket ID")
    booking_id: str = Field(..., description="Booking ID")
    status: BoardingPassStatus = Field(default=BoardingPassStatus.ISSUED)
    boarding_number: str = Field(..., description="Boarding number")
    boarding_time: datetime = Field(..., description="Boarding time")
    gate: Optional[str] = None
    seat_number: str = Field(..., description="Seat number")
    passenger_name: str = Field(..., description="Passenger name")
    route_from: str = Field(..., description="Route from")
    route_to: str = Field(..., description="Route to")
    journey_date: datetime = Field(..., description="Journey date")
    vehicle_number: str = Field(..., description="Vehicle number")
    qr_code: str = Field(..., description="QR code data")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "BP-001",
                "ticket_id": "TK-001",
                "booking_id": "BK-001",
                "status": "issued",
                "boarding_number": "BP001",
                "seat_number": "A1",
                "passenger_name": "John Doe"
            }
        }


class VerificationLog(BaseModel):
    """Verification log model"""
    id: str = Field(..., description="Unique log ID")
    ticket_id: str = Field(..., description="Ticket ID")
    verification_status: VerificationStatus = Field(..., description="Verification status")
    verified_at: datetime = Field(default_factory=datetime.utcnow)
    verified_by: str = Field(..., description="Verified by (staff ID)")
    verification_location: str = Field(..., description="Verification location")
    device_id: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "LOG-001",
                "ticket_id": "TK-001",
                "verification_status": "valid",
                "verified_by": "STAFF-001",
                "verification_location": "Gate A"
            }
        }


class VerifyTicketRequest(BaseModel):
    """Request model for verifying a ticket"""
    qr_code: str
    verified_by: str
    verification_location: str


class GenerateBoardingPassRequest(BaseModel):
    """Request model for generating a boarding pass"""
    ticket_id: str
    boarding_time: datetime


class VerificationResponse(BaseModel):
    """Response model for verification operations"""
    success: bool
    message: str
    data: Optional[TicketVerification] = None


class BoardingPassResponse(BaseModel):
    """Response model for boarding pass operations"""
    success: bool
    message: str
    data: Optional[BoardingPass] = None
