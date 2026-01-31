"""
Commerce Models

Data models for core commerce operations including orders and transactions.
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    """Order status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class TransactionStatus(str, Enum):
    """Transaction status enumeration"""
    INITIATED = "initiated"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class OrderItem(BaseModel):
    """Individual item in an order"""
    product_id: str
    quantity: int
    unit_price: float
    total_price: float
    sku: Optional[str] = None


class Order(BaseModel):
    """Order model"""
    id: str = Field(..., description="Unique order ID")
    customer_id: str = Field(..., description="Customer ID")
    items: List[OrderItem] = Field(..., description="Order items")
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="Order status")
    subtotal: float = Field(..., description="Subtotal before taxes/fees")
    tax: float = Field(default=0.0, description="Tax amount")
    shipping: float = Field(default=0.0, description="Shipping cost")
    total: float = Field(..., description="Total order amount")
    shipping_address: Dict[str, Any] = Field(..., description="Shipping address")
    billing_address: Dict[str, Any] = Field(..., description="Billing address")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "ORD-001",
                "customer_id": "CUST-001",
                "items": [
                    {
                        "product_id": "PROD-001",
                        "quantity": 2,
                        "unit_price": 29.99,
                        "total_price": 59.98,
                        "sku": "SKU-001"
                    }
                ],
                "status": "confirmed",
                "subtotal": 59.98,
                "tax": 4.80,
                "shipping": 10.00,
                "total": 74.78,
                "shipping_address": {
                    "street": "123 Main St",
                    "city": "Springfield",
                    "state": "IL",
                    "zip": "62701"
                },
                "billing_address": {
                    "street": "123 Main St",
                    "city": "Springfield",
                    "state": "IL",
                    "zip": "62701"
                }
            }
        }


class Transaction(BaseModel):
    """Transaction model"""
    id: str = Field(..., description="Unique transaction ID")
    order_id: str = Field(..., description="Associated order ID")
    customer_id: str = Field(..., description="Customer ID")
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(default="USD", description="Currency code")
    status: TransactionStatus = Field(default=TransactionStatus.INITIATED)
    payment_method: str = Field(..., description="Payment method (card, wallet, etc)")
    payment_gateway: str = Field(..., description="Payment gateway used")
    reference_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "TXN-001",
                "order_id": "ORD-001",
                "customer_id": "CUST-001",
                "amount": 74.78,
                "currency": "USD",
                "status": "completed",
                "payment_method": "credit_card",
                "payment_gateway": "stripe",
                "reference_id": "ch_1234567890"
            }
        }


class CreateOrderRequest(BaseModel):
    """Request model for creating an order"""
    customer_id: str
    items: List[OrderItem]
    shipping_address: Dict[str, Any]
    billing_address: Dict[str, Any]
    notes: Optional[str] = None


class UpdateOrderRequest(BaseModel):
    """Request model for updating an order"""
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None


class CreateTransactionRequest(BaseModel):
    """Request model for creating a transaction"""
    order_id: str
    customer_id: str
    amount: float
    payment_method: str
    payment_gateway: str


class OrderResponse(BaseModel):
    """Response model for order operations"""
    success: bool
    message: str
    data: Optional[Order] = None


class TransactionResponse(BaseModel):
    """Response model for transaction operations"""
    success: bool
    message: str
    data: Optional[Transaction] = None
