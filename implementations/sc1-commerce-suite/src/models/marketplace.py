"""
Marketplace Models

Data models for Single Vendor Marketplace (SVM) and Multi-Vendor Marketplace (MVM).
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MarketplaceType(str, Enum):
    """Marketplace type enumeration"""
    SVM = "svm"  # Single Vendor Marketplace
    MVM = "mvm"  # Multi-Vendor Marketplace


class VendorStatus(str, Enum):
    """Vendor status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class ProductStatus(str, Enum):
    """Product status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"


class Vendor(BaseModel):
    """Vendor model for MVM"""
    id: str = Field(..., description="Unique vendor ID")
    name: str = Field(..., description="Vendor name")
    email: str = Field(..., description="Vendor email")
    status: VendorStatus = Field(default=VendorStatus.PENDING)
    commission_rate: float = Field(default=0.0, description="Commission percentage")
    total_sales: float = Field(default=0.0, description="Total sales amount")
    rating: float = Field(default=0.0, description="Vendor rating (0-5)")
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    contact_info: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "VENDOR-001",
                "name": "Premium Electronics",
                "email": "vendor@example.com",
                "status": "active",
                "commission_rate": 15.0,
                "total_sales": 50000.00,
                "rating": 4.8,
                "description": "Leading electronics retailer"
            }
        }


class Product(BaseModel):
    """Product model"""
    id: str = Field(..., description="Unique product ID")
    sku: str = Field(..., description="Stock Keeping Unit")
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Product description")
    category: str = Field(..., description="Product category")
    price: float = Field(..., description="Product price")
    cost: Optional[float] = None
    status: ProductStatus = Field(default=ProductStatus.ACTIVE)
    vendor_id: Optional[str] = None  # Only for MVM
    images: List[str] = Field(default_factory=list, description="Product image URLs")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Product attributes")
    rating: float = Field(default=0.0, description="Product rating (0-5)")
    reviews_count: int = Field(default=0, description="Number of reviews")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "PROD-001",
                "sku": "SKU-001",
                "name": "Wireless Headphones",
                "description": "High-quality wireless headphones",
                "category": "Electronics",
                "price": 99.99,
                "cost": 50.00,
                "status": "active",
                "vendor_id": "VENDOR-001",
                "rating": 4.5,
                "reviews_count": 150
            }
        }


class Listing(BaseModel):
    """Product listing model"""
    id: str = Field(..., description="Unique listing ID")
    product_id: str = Field(..., description="Product ID")
    vendor_id: str = Field(..., description="Vendor ID (for MVM)")
    marketplace_type: MarketplaceType = Field(..., description="Marketplace type")
    quantity_available: int = Field(..., description="Available quantity")
    price: float = Field(..., description="Listing price")
    status: ProductStatus = Field(default=ProductStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "LIST-001",
                "product_id": "PROD-001",
                "vendor_id": "VENDOR-001",
                "marketplace_type": "mvm",
                "quantity_available": 100,
                "price": 99.99,
                "status": "active"
            }
        }


class CreateVendorRequest(BaseModel):
    """Request model for creating a vendor"""
    name: str
    email: str
    commission_rate: float
    description: Optional[str] = None
    website: Optional[str] = None


class UpdateVendorRequest(BaseModel):
    """Request model for updating a vendor"""
    name: Optional[str] = None
    status: Optional[VendorStatus] = None
    commission_rate: Optional[float] = None
    description: Optional[str] = None


class CreateProductRequest(BaseModel):
    """Request model for creating a product"""
    sku: str
    name: str
    description: str
    category: str
    price: float
    cost: Optional[float] = None
    vendor_id: Optional[str] = None


class UpdateProductRequest(BaseModel):
    """Request model for updating a product"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    status: Optional[ProductStatus] = None


class VendorResponse(BaseModel):
    """Response model for vendor operations"""
    success: bool
    message: str
    data: Optional[Vendor] = None


class ProductResponse(BaseModel):
    """Response model for product operations"""
    success: bool
    message: str
    data: Optional[Product] = None


class ListingResponse(BaseModel):
    """Response model for listing operations"""
    success: bool
    message: str
    data: Optional[Listing] = None
