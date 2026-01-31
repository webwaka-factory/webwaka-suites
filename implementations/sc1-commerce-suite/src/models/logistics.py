"""
Logistics Models

Data models for logistics, shipments, and carrier management.
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DeliveryStatus(str, Enum):
    """Delivery status enumeration"""
    PENDING = "pending"
    PICKED = "picked"
    PACKED = "packed"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"


class CarrierType(str, Enum):
    """Carrier type enumeration"""
    STANDARD = "standard"
    EXPRESS = "express"
    OVERNIGHT = "overnight"
    INTERNATIONAL = "international"


class Carrier(BaseModel):
    """Carrier model"""
    id: str = Field(..., description="Unique carrier ID")
    name: str = Field(..., description="Carrier name")
    code: str = Field(..., description="Carrier code")
    carrier_type: CarrierType = Field(..., description="Carrier type")
    base_rate: float = Field(..., description="Base shipping rate")
    active: bool = Field(default=True, description="Is carrier active")
    api_key: Optional[str] = None
    contact_info: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "CARRIER-001",
                "name": "Express Delivery Co",
                "code": "EDC",
                "carrier_type": "express",
                "base_rate": 5.99,
                "active": True
            }
        }


class TrackingEvent(BaseModel):
    """Tracking event model"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: DeliveryStatus = Field(..., description="Status at this point")
    location: Optional[str] = None
    description: Optional[str] = None


class Shipment(BaseModel):
    """Shipment model"""
    id: str = Field(..., description="Unique shipment ID")
    order_id: str = Field(..., description="Associated order ID")
    tracking_number: str = Field(..., description="Carrier tracking number")
    carrier_id: str = Field(..., description="Carrier ID")
    status: DeliveryStatus = Field(default=DeliveryStatus.PENDING)
    origin_address: Dict[str, Any] = Field(..., description="Origin address")
    destination_address: Dict[str, Any] = Field(..., description="Destination address")
    weight: float = Field(..., description="Shipment weight (kg)")
    dimensions: Dict[str, float] = Field(..., description="Shipment dimensions (L x W x H)")
    cost: float = Field(..., description="Shipping cost")
    estimated_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    tracking_events: List[TrackingEvent] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "SHIP-001",
                "order_id": "ORD-001",
                "tracking_number": "1Z999AA10123456784",
                "carrier_id": "CARRIER-001",
                "status": "in_transit",
                "weight": 2.5,
                "cost": 15.99
            }
        }


class Return(BaseModel):
    """Return model"""
    id: str = Field(..., description="Unique return ID")
    order_id: str = Field(..., description="Original order ID")
    shipment_id: Optional[str] = None
    reason: str = Field(..., description="Return reason")
    status: DeliveryStatus = Field(default=DeliveryStatus.PENDING)
    return_address: Dict[str, Any] = Field(..., description="Return address")
    refund_amount: float = Field(..., description="Refund amount")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "RET-001",
                "order_id": "ORD-001",
                "reason": "Defective product",
                "status": "pending",
                "refund_amount": 99.99
            }
        }


class CreateShipmentRequest(BaseModel):
    """Request model for creating a shipment"""
    order_id: str
    carrier_id: str
    origin_address: Dict[str, Any]
    destination_address: Dict[str, Any]
    weight: float
    dimensions: Dict[str, float]


class UpdateShipmentRequest(BaseModel):
    """Request model for updating a shipment"""
    status: Optional[DeliveryStatus] = None
    tracking_number: Optional[str] = None


class CreateReturnRequest(BaseModel):
    """Request model for creating a return"""
    order_id: str
    reason: str
    return_address: Dict[str, Any]


class ShipmentResponse(BaseModel):
    """Response model for shipment operations"""
    success: bool
    message: str
    data: Optional[Shipment] = None


class ReturnResponse(BaseModel):
    """Response model for return operations"""
    success: bool
    message: str
    data: Optional[Return] = None
