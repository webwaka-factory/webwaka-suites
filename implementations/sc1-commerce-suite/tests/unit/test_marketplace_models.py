"""
Unit Tests for SC-1 Marketplace Models

Tests for Vendor, Product, Listing, and related models for SVM and MVM.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.models.marketplace import (
    Vendor, Product, Listing, MarketplaceType, VendorStatus, ProductStatus,
    CreateVendorRequest, UpdateVendorRequest, CreateProductRequest,
    UpdateProductRequest, VendorResponse, ProductResponse, ListingResponse
)


class TestMarketplaceType:
    """Tests for MarketplaceType enum"""

    def test_marketplace_type_values(self):
        """Test marketplace type values"""
        assert MarketplaceType.SVM == "svm"
        assert MarketplaceType.MVM == "mvm"


class TestVendorStatus:
    """Tests for VendorStatus enum"""

    def test_vendor_status_values(self):
        """Test all vendor status values exist"""
        assert VendorStatus.PENDING == "pending"
        assert VendorStatus.APPROVED == "approved"
        assert VendorStatus.ACTIVE == "active"
        assert VendorStatus.SUSPENDED == "suspended"
        assert VendorStatus.INACTIVE == "inactive"


class TestProductStatus:
    """Tests for ProductStatus enum"""

    def test_product_status_values(self):
        """Test all product status values exist"""
        assert ProductStatus.DRAFT == "draft"
        assert ProductStatus.ACTIVE == "active"
        assert ProductStatus.INACTIVE == "inactive"
        assert ProductStatus.DISCONTINUED == "discontinued"


class TestVendor:
    """Tests for Vendor model"""

    def test_create_vendor(self):
        """Test creating a valid vendor"""
        vendor = Vendor(
            id="VENDOR-001",
            name="Premium Electronics",
            email="vendor@example.com"
        )
        
        assert vendor.id == "VENDOR-001"
        assert vendor.name == "Premium Electronics"
        assert vendor.email == "vendor@example.com"
        assert vendor.status == VendorStatus.PENDING

    def test_vendor_default_values(self):
        """Test vendor default values"""
        vendor = Vendor(
            id="VENDOR-001",
            name="Test Vendor",
            email="test@example.com"
        )
        
        assert vendor.commission_rate == 0.0
        assert vendor.total_sales == 0.0
        assert vendor.rating == 0.0

    def test_vendor_with_full_details(self, sample_vendor):
        """Test vendor with full details"""
        assert sample_vendor.status == VendorStatus.ACTIVE
        assert sample_vendor.commission_rate == 15.0
        assert sample_vendor.rating == 4.8
        assert sample_vendor.total_sales == 5000000.00

    def test_vendor_nigeria_based(self):
        """Test Nigeria-based vendor (INV-007)"""
        vendor = Vendor(
            id="VENDOR-NG-001",
            name="Lagos Electronics Hub",
            email="vendor@lagos.ng",
            status=VendorStatus.ACTIVE,
            description="Premier electronics retailer in Lagos, Nigeria",
            contact_info={
                "phone": "+234-800-123-4567",
                "address": "123 Victoria Island, Lagos, Nigeria"
            }
        )
        
        assert "Nigeria" in vendor.description
        assert "+234" in vendor.contact_info["phone"]

    def test_vendor_timestamps(self, sample_vendor):
        """Test vendor has timestamps"""
        assert sample_vendor.created_at is not None
        assert sample_vendor.updated_at is not None

    def test_vendor_json_serialization(self, sample_vendor):
        """Test vendor can be serialized to JSON"""
        json_data = sample_vendor.model_dump_json()
        assert "VENDOR-001" in json_data
        assert "Premium Electronics Nigeria" in json_data


class TestProduct:
    """Tests for Product model"""

    def test_create_product(self):
        """Test creating a valid product"""
        product = Product(
            id="PROD-001",
            sku="SKU-001",
            name="Wireless Headphones",
            description="High-quality wireless headphones",
            category="Electronics",
            price=99.99
        )
        
        assert product.id == "PROD-001"
        assert product.name == "Wireless Headphones"
        assert product.price == 99.99
        assert product.status == ProductStatus.ACTIVE

    def test_product_default_values(self):
        """Test product default values"""
        product = Product(
            id="PROD-001",
            sku="SKU-001",
            name="Test Product",
            description="Test description",
            category="Test",
            price=10.00
        )
        
        assert product.rating == 0.0
        assert product.reviews_count == 0
        assert product.images == []
        assert product.attributes == {}

    def test_product_with_vendor(self, sample_product):
        """Test product with vendor (MVM)"""
        assert sample_product.vendor_id == "VENDOR-001"

    def test_product_without_vendor(self):
        """Test product without vendor (SVM)"""
        product = Product(
            id="PROD-001",
            sku="SKU-001",
            name="Store Product",
            description="Single vendor product",
            category="General",
            price=50.00
        )
        
        assert product.vendor_id is None

    def test_product_with_images(self):
        """Test product with images"""
        product = Product(
            id="PROD-001",
            sku="SKU-001",
            name="Product with Images",
            description="Has multiple images",
            category="Fashion",
            price=75.00,
            images=[
                "https://cdn.example.com/img1.jpg",
                "https://cdn.example.com/img2.jpg"
            ]
        )
        
        assert len(product.images) == 2

    def test_product_with_attributes(self):
        """Test product with attributes"""
        product = Product(
            id="PROD-001",
            sku="SKU-001",
            name="Configurable Product",
            description="Has attributes",
            category="Electronics",
            price=150.00,
            attributes={
                "color": "Black",
                "size": "Large",
                "weight": "500g"
            }
        )
        
        assert product.attributes["color"] == "Black"
        assert product.attributes["size"] == "Large"

    def test_product_nigeria_pricing(self):
        """Test product with Nigeria pricing (INV-007)"""
        product = Product(
            id="PROD-NG-001",
            sku="SKU-NG-001",
            name="Nigerian Product",
            description="Product priced in Naira",
            category="Electronics",
            price=25000.00,  # NGN
            cost=15000.00    # NGN
        )
        
        assert product.price == 25000.00
        assert product.cost == 15000.00

    def test_product_timestamps(self, sample_product):
        """Test product has timestamps"""
        assert sample_product.created_at is not None
        assert sample_product.updated_at is not None


class TestListing:
    """Tests for Listing model"""

    def test_create_listing(self):
        """Test creating a valid listing"""
        listing = Listing(
            id="LIST-001",
            product_id="PROD-001",
            vendor_id="VENDOR-001",
            marketplace_type=MarketplaceType.MVM,
            quantity_available=100,
            price=99.99
        )
        
        assert listing.id == "LIST-001"
        assert listing.marketplace_type == MarketplaceType.MVM
        assert listing.status == ProductStatus.ACTIVE

    def test_listing_svm(self):
        """Test listing for Single Vendor Marketplace"""
        listing = Listing(
            id="LIST-001",
            product_id="PROD-001",
            vendor_id="OWNER",
            marketplace_type=MarketplaceType.SVM,
            quantity_available=50,
            price=49.99
        )
        
        assert listing.marketplace_type == MarketplaceType.SVM

    def test_listing_mvm(self, sample_listing):
        """Test listing for Multi-Vendor Marketplace"""
        assert sample_listing.marketplace_type == MarketplaceType.MVM
        assert sample_listing.vendor_id == "VENDOR-001"

    def test_listing_timestamps(self, sample_listing):
        """Test listing has timestamps"""
        assert sample_listing.created_at is not None
        assert sample_listing.updated_at is not None


class TestCreateVendorRequest:
    """Tests for CreateVendorRequest model"""

    def test_create_vendor_request(self):
        """Test creating vendor request"""
        request = CreateVendorRequest(
            name="New Vendor",
            email="new@vendor.com",
            commission_rate=10.0
        )
        
        assert request.name == "New Vendor"
        assert request.email == "new@vendor.com"
        assert request.commission_rate == 10.0

    def test_create_vendor_request_with_optional(self):
        """Test vendor request with optional fields"""
        request = CreateVendorRequest(
            name="Full Vendor",
            email="full@vendor.com",
            commission_rate=12.5,
            description="A full featured vendor",
            website="https://vendor.com"
        )
        
        assert request.description == "A full featured vendor"
        assert request.website == "https://vendor.com"


class TestUpdateVendorRequest:
    """Tests for UpdateVendorRequest model"""

    def test_update_vendor_status(self):
        """Test updating vendor status"""
        request = UpdateVendorRequest(status=VendorStatus.ACTIVE)
        assert request.status == VendorStatus.ACTIVE

    def test_update_vendor_commission(self):
        """Test updating vendor commission"""
        request = UpdateVendorRequest(commission_rate=20.0)
        assert request.commission_rate == 20.0

    def test_partial_vendor_update(self):
        """Test partial vendor update"""
        request = UpdateVendorRequest(name="Updated Name")
        
        assert request.name == "Updated Name"
        assert request.status is None
        assert request.commission_rate is None


class TestCreateProductRequest:
    """Tests for CreateProductRequest model"""

    def test_create_product_request(self):
        """Test creating product request"""
        request = CreateProductRequest(
            sku="SKU-NEW-001",
            name="New Product",
            description="A new product",
            category="Electronics",
            price=199.99
        )
        
        assert request.sku == "SKU-NEW-001"
        assert request.name == "New Product"
        assert request.price == 199.99

    def test_create_product_request_with_vendor(self):
        """Test product request with vendor (MVM)"""
        request = CreateProductRequest(
            sku="SKU-MVM-001",
            name="Vendor Product",
            description="Product from vendor",
            category="Fashion",
            price=75.00,
            vendor_id="VENDOR-001"
        )
        
        assert request.vendor_id == "VENDOR-001"

    def test_create_product_request_with_cost(self):
        """Test product request with cost"""
        request = CreateProductRequest(
            sku="SKU-COST-001",
            name="Product with Cost",
            description="Has cost tracking",
            category="General",
            price=100.00,
            cost=60.00
        )
        
        assert request.cost == 60.00


class TestUpdateProductRequest:
    """Tests for UpdateProductRequest model"""

    def test_update_product_price(self):
        """Test updating product price"""
        request = UpdateProductRequest(price=149.99)
        assert request.price == 149.99

    def test_update_product_status(self):
        """Test updating product status"""
        request = UpdateProductRequest(status=ProductStatus.DISCONTINUED)
        assert request.status == ProductStatus.DISCONTINUED

    def test_partial_product_update(self):
        """Test partial product update"""
        request = UpdateProductRequest(description="Updated description")
        
        assert request.description == "Updated description"
        assert request.name is None
        assert request.price is None


class TestVendorResponse:
    """Tests for VendorResponse model"""

    def test_successful_vendor_response(self, sample_vendor):
        """Test successful vendor response"""
        response = VendorResponse(
            success=True,
            message="Vendor created successfully",
            data=sample_vendor
        )
        
        assert response.success is True
        assert response.data is not None
        assert response.data.id == "VENDOR-001"

    def test_failed_vendor_response(self):
        """Test failed vendor response"""
        response = VendorResponse(
            success=False,
            message="Vendor not found"
        )
        
        assert response.success is False
        assert response.data is None


class TestProductResponse:
    """Tests for ProductResponse model"""

    def test_successful_product_response(self, sample_product):
        """Test successful product response"""
        response = ProductResponse(
            success=True,
            message="Product retrieved",
            data=sample_product
        )
        
        assert response.success is True
        assert response.data is not None
        assert response.data.id == "PROD-001"

    def test_failed_product_response(self):
        """Test failed product response"""
        response = ProductResponse(
            success=False,
            message="Product not found"
        )
        
        assert response.success is False
        assert response.data is None


class TestListingResponse:
    """Tests for ListingResponse model"""

    def test_successful_listing_response(self, sample_listing):
        """Test successful listing response"""
        response = ListingResponse(
            success=True,
            message="Listing created",
            data=sample_listing
        )
        
        assert response.success is True
        assert response.data is not None
        assert response.data.id == "LIST-001"

    def test_failed_listing_response(self):
        """Test failed listing response"""
        response = ListingResponse(
            success=False,
            message="Listing not found"
        )
        
        assert response.success is False
        assert response.data is None
