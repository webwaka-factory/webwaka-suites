"""
Marketplace Models

Data models for transport marketplaces (SVM and MVM).
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class OperatorStatus(str, Enum):
    """Operator status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class RouteStatus(str, Enum):
    """Route status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class TransportOperator(BaseModel):
    """Transport operator model"""
    id: str = Field(..., description="Unique operator ID")
    name: str = Field(..., description="Operator name")
    email: str = Field(..., description="Operator email")
    phone: str = Field(..., description="Operator phone")
    status: OperatorStatus = Field(default=OperatorStatus.PENDING)
    commission_rate: float = Field(default=0.0, description="Commission percentage")
    total_bookings: int = Field(default=0, description="Total bookings")
    rating: float = Field(default=0.0, description="Operator rating (0-5)")
    license_number: str = Field(..., description="Transport license number")
    address: Dict[str, Any] = Field(..., description="Operator address")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "OP-001",
                "name": "Express Transport Co",
                "email": "operator@example.com",
                "phone": "+1234567890",
                "status": "active",
                "commission_rate": 10.0,
                "license_number": "LIC-001"
            }
        }


class Route(BaseModel):
    """Route model"""
    id: str = Field(..., description="Unique route ID")
    operator_id: str = Field(..., description="Operator ID")
    origin: str = Field(..., description="Origin city")
    destination: str = Field(..., description="Destination city")
    status: RouteStatus = Field(default=RouteStatus.ACTIVE)
    departure_time: str = Field(..., description="Departure time (HH:MM)")
    arrival_time: str = Field(..., description="Arrival time (HH:MM)")
    duration_hours: float = Field(..., description="Journey duration in hours")
    base_price: float = Field(..., description="Base ticket price")
    available_seats: int = Field(..., description="Available seats")
    total_seats: int = Field(..., description="Total seats")
    vehicle_type: str = Field(..., description="Vehicle type")
    amenities: List[str] = Field(default_factory=list, description="Amenities")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "RT-001",
                "operator_id": "OP-001",
                "origin": "Lagos",
                "destination": "Ibadan",
                "departure_time": "08:00",
                "arrival_time": "10:30",
                "duration_hours": 2.5,
                "base_price": 25.00,
                "available_seats": 40,
                "total_seats": 50,
                "vehicle_type": "Coach"
            }
        }


class Schedule(BaseModel):
    """Schedule model"""
    id: str = Field(..., description="Unique schedule ID")
    route_id: str = Field(..., description="Route ID")
    date: str = Field(..., description="Schedule date (YYYY-MM-DD)")
    departure_time: str = Field(..., description="Departure time (HH:MM)")
    available_seats: int = Field(..., description="Available seats")
    total_seats: int = Field(..., description="Total seats")
    vehicle_id: str = Field(..., description="Vehicle ID")
    status: RouteStatus = Field(default=RouteStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "SCH-001",
                "route_id": "RT-001",
                "date": "2024-01-30",
                "departure_time": "08:00",
                "available_seats": 40,
                "total_seats": 50,
                "vehicle_id": "VEH-001"
            }
        }


class Vehicle(BaseModel):
    """Vehicle model"""
    id: str = Field(..., description="Unique vehicle ID")
    operator_id: str = Field(..., description="Operator ID")
    registration_number: str = Field(..., description="Vehicle registration number")
    vehicle_type: str = Field(..., description="Vehicle type")
    total_seats: int = Field(..., description="Total seats")
    year: int = Field(..., description="Year of manufacture")
    last_service_date: Optional[datetime] = None
    status: str = Field(default="active", description="Vehicle status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "VEH-001",
                "operator_id": "OP-001",
                "registration_number": "ABC-123",
                "vehicle_type": "Coach",
                "total_seats": 50,
                "year": 2023
            }
        }


class CreateOperatorRequest(BaseModel):
    """Request model for creating an operator"""
    name: str
    email: str
    phone: str
    license_number: str
    address: Dict[str, Any]


class CreateRouteRequest(BaseModel):
    """Request model for creating a route"""
    operator_id: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    base_price: float
    total_seats: int
    vehicle_type: str


class OperatorResponse(BaseModel):
    """Response model for operator operations"""
    success: bool
    message: str
    data: Optional[TransportOperator] = None


class RouteResponse(BaseModel):
    """Response model for route operations"""
    success: bool
    message: str
    data: Optional[Route] = None


class ScheduleResponse(BaseModel):
    """Response model for schedule operations"""
    success: bool
    message: str
    data: Optional[Schedule] = None
