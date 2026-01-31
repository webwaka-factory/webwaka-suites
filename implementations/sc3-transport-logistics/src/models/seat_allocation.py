"""
Seat Allocation Models

Data models for seat allocation and management.
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SeatStatus(str, Enum):
    """Seat status enumeration"""
    AVAILABLE = "available"
    HELD = "held"
    BOOKED = "booked"
    BLOCKED = "blocked"


class SeatType(str, Enum):
    """Seat type enumeration"""
    STANDARD = "standard"
    PREMIUM = "premium"
    ACCESSIBILITY = "accessibility"


class Seat(BaseModel):
    """Seat model"""
    id: str = Field(..., description="Unique seat ID")
    vehicle_id: str = Field(..., description="Vehicle ID")
    seat_number: str = Field(..., description="Seat number")
    row: int = Field(..., description="Row number")
    column: int = Field(..., description="Column number")
    seat_type: SeatType = Field(default=SeatType.STANDARD)
    status: SeatStatus = Field(default=SeatStatus.AVAILABLE)
    price: float = Field(..., description="Seat price")
    held_by: Optional[str] = None
    held_until: Optional[datetime] = None
    booked_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "SEAT-001",
                "vehicle_id": "VEH-001",
                "seat_number": "A1",
                "row": 1,
                "column": 1,
                "seat_type": "standard",
                "status": "available",
                "price": 25.00
            }
        }


class SeatMap(BaseModel):
    """Seat map model"""
    id: str = Field(..., description="Unique seat map ID")
    vehicle_id: str = Field(..., description="Vehicle ID")
    total_seats: int = Field(..., description="Total seats")
    rows: int = Field(..., description="Number of rows")
    columns: int = Field(..., description="Number of columns")
    seats: List[Seat] = Field(..., description="Seat list")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "MAP-001",
                "vehicle_id": "VEH-001",
                "total_seats": 50,
                "rows": 10,
                "columns": 5,
                "seats": []
            }
        }


class SeatHold(BaseModel):
    """Seat hold model"""
    id: str = Field(..., description="Unique hold ID")
    seat_id: str = Field(..., description="Seat ID")
    held_by: str = Field(..., description="Customer ID")
    held_at: datetime = Field(default_factory=datetime.utcnow)
    hold_expires_at: datetime = Field(..., description="Hold expiration time")
    booking_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "HOLD-001",
                "seat_id": "SEAT-001",
                "held_by": "CUST-001",
                "hold_expires_at": "2024-01-30T21:00:00"
            }
        }


class UpdateSeatRequest(BaseModel):
    """Request model for updating a seat"""
    status: Optional[SeatStatus] = None
    price: Optional[float] = None


class HoldSeatRequest(BaseModel):
    """Request model for holding a seat"""
    customer_id: str
    hold_duration_minutes: int = 15


class BookSeatRequest(BaseModel):
    """Request model for booking a seat"""
    customer_id: str
    booking_id: str


class SeatResponse(BaseModel):
    """Response model for seat operations"""
    success: bool
    message: str
    data: Optional[Seat] = None


class SeatMapResponse(BaseModel):
    """Response model for seat map operations"""
    success: bool
    message: str
    data: Optional[SeatMap] = None
