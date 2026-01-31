"""
Customer Engagement Models

Data models for loyalty programs, coupons, subscriptions, and refunds.
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class LoyaltyStatus(str, Enum):
    """Loyalty program status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class CouponStatus(str, Enum):
    """Coupon status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    USED = "used"


class SubscriptionStatus(str, Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class RefundStatus(str, Enum):
    """Refund status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"


class LoyaltyProgram(BaseModel):
    """Loyalty program model"""
    id: str = Field(..., description="Unique loyalty program ID")
    customer_id: str = Field(..., description="Customer ID")
    status: LoyaltyStatus = Field(default=LoyaltyStatus.ACTIVE)
    points_balance: int = Field(default=0, description="Current points balance")
    lifetime_points: int = Field(default=0, description="Lifetime points earned")
    tier: str = Field(default="bronze", description="Loyalty tier")
    joined_date: datetime = Field(default_factory=datetime.utcnow)
    last_activity: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "LOYALTY-001",
                "customer_id": "CUST-001",
                "status": "active",
                "points_balance": 500,
                "lifetime_points": 2000,
                "tier": "silver"
            }
        }


class Coupon(BaseModel):
    """Coupon model"""
    id: str = Field(..., description="Unique coupon ID")
    code: str = Field(..., description="Coupon code")
    description: str = Field(..., description="Coupon description")
    status: CouponStatus = Field(default=CouponStatus.ACTIVE)
    discount_type: str = Field(..., description="Discount type (percentage or fixed)")
    discount_value: float = Field(..., description="Discount value")
    max_uses: Optional[int] = None
    current_uses: int = Field(default=0)
    min_order_value: float = Field(default=0.0)
    valid_from: datetime = Field(..., description="Valid from date")
    valid_until: datetime = Field(..., description="Valid until date")
    applicable_products: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "COUPON-001",
                "code": "SAVE20",
                "description": "20% off all items",
                "status": "active",
                "discount_type": "percentage",
                "discount_value": 20.0,
                "max_uses": 1000,
                "current_uses": 250
            }
        }


class Subscription(BaseModel):
    """Subscription model"""
    id: str = Field(..., description="Unique subscription ID")
    customer_id: str = Field(..., description="Customer ID")
    product_id: str = Field(..., description="Product ID")
    status: SubscriptionStatus = Field(default=SubscriptionStatus.ACTIVE)
    plan: str = Field(..., description="Subscription plan")
    billing_cycle: str = Field(..., description="Billing cycle (monthly, yearly, etc)")
    price: float = Field(..., description="Subscription price")
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    next_billing_date: datetime = Field(..., description="Next billing date")
    auto_renew: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "SUB-001",
                "customer_id": "CUST-001",
                "product_id": "PROD-001",
                "status": "active",
                "plan": "premium",
                "billing_cycle": "monthly",
                "price": 9.99,
                "auto_renew": True
            }
        }


class Refund(BaseModel):
    """Refund model"""
    id: str = Field(..., description="Unique refund ID")
    order_id: str = Field(..., description="Associated order ID")
    customer_id: str = Field(..., description="Customer ID")
    amount: float = Field(..., description="Refund amount")
    reason: str = Field(..., description="Refund reason")
    status: RefundStatus = Field(default=RefundStatus.PENDING)
    notes: Optional[str] = None
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "REFUND-001",
                "order_id": "ORD-001",
                "customer_id": "CUST-001",
                "amount": 99.99,
                "reason": "Defective product",
                "status": "approved"
            }
        }


class CreateLoyaltyProgramRequest(BaseModel):
    """Request model for creating a loyalty program"""
    customer_id: str


class CreateCouponRequest(BaseModel):
    """Request model for creating a coupon"""
    code: str
    description: str
    discount_type: str
    discount_value: float
    valid_from: datetime
    valid_until: datetime


class CreateSubscriptionRequest(BaseModel):
    """Request model for creating a subscription"""
    customer_id: str
    product_id: str
    plan: str
    billing_cycle: str
    price: float


class CreateRefundRequest(BaseModel):
    """Request model for creating a refund"""
    order_id: str
    customer_id: str
    amount: float
    reason: str


class LoyaltyResponse(BaseModel):
    """Response model for loyalty operations"""
    success: bool
    message: str
    data: Optional[LoyaltyProgram] = None


class CouponResponse(BaseModel):
    """Response model for coupon operations"""
    success: bool
    message: str
    data: Optional[Coupon] = None


class SubscriptionResponse(BaseModel):
    """Response model for subscription operations"""
    success: bool
    message: str
    data: Optional[Subscription] = None


class RefundResponse(BaseModel):
    """Response model for refund operations"""
    success: bool
    message: str
    data: Optional[Refund] = None
