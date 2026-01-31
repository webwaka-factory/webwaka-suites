"""
SC-1 Commerce Suite Test Configuration

Shared fixtures and configuration for all tests.
"""

import pytest
from datetime import datetime
from typing import Dict, Any
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Import the FastAPI app
import sys
sys.path.insert(0, str(__file__).replace('/tests/conftest.py', ''))
from src.api.server import app

# Import models
from src.models.commerce import (
    Order, OrderItem, OrderStatus, Transaction, TransactionStatus,
    CreateOrderRequest
)
from src.models.inventory import (
    InventoryItem, StockLevel, InventorySyncConfig, SyncTarget, SyncStatus
)
from src.models.marketplace import (
    Vendor, Product, Listing, VendorStatus, ProductStatus, MarketplaceType
)


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create an async test client for the FastAPI app"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_order_item() -> OrderItem:
    """Create a sample order item"""
    return OrderItem(
        product_id="PROD-001",
        quantity=2,
        unit_price=29.99,
        total_price=59.98,
        sku="SKU-001"
    )


@pytest.fixture
def sample_shipping_address() -> Dict[str, Any]:
    """Create a sample shipping address"""
    return {
        "street": "123 Main Street",
        "city": "Lagos",
        "state": "Lagos",
        "country": "Nigeria",
        "postal_code": "100001"
    }


@pytest.fixture
def sample_billing_address() -> Dict[str, Any]:
    """Create a sample billing address"""
    return {
        "street": "123 Main Street",
        "city": "Lagos",
        "state": "Lagos",
        "country": "Nigeria",
        "postal_code": "100001"
    }


@pytest.fixture
def sample_order(sample_order_item, sample_shipping_address, sample_billing_address) -> Order:
    """Create a sample order"""
    return Order(
        id="ORD-001",
        customer_id="CUST-001",
        items=[sample_order_item],
        status=OrderStatus.PENDING,
        subtotal=59.98,
        tax=4.80,
        shipping=10.00,
        total=74.78,
        shipping_address=sample_shipping_address,
        billing_address=sample_billing_address
    )


@pytest.fixture
def sample_transaction() -> Transaction:
    """Create a sample transaction"""
    return Transaction(
        id="TXN-001",
        order_id="ORD-001",
        customer_id="CUST-001",
        amount=74.78,
        currency="NGN",
        status=TransactionStatus.INITIATED,
        payment_method="card",
        payment_gateway="paystack"
    )


@pytest.fixture
def sample_inventory_item() -> InventoryItem:
    """Create a sample inventory item"""
    return InventoryItem(
        id="INV-001",
        product_id="PROD-001",
        sku="SKU-001",
        location="Warehouse Lagos",
        quantity_on_hand=100,
        quantity_reserved=10,
        quantity_available=90,
        reorder_point=20,
        reorder_quantity=100
    )


@pytest.fixture
def sample_sync_config() -> InventorySyncConfig:
    """Create a sample sync configuration"""
    return InventorySyncConfig(
        id="SYNC-001",
        enabled=True,
        sync_targets=[SyncTarget.POS, SyncTarget.SVM, SyncTarget.MVM],
        sync_frequency="realtime"
    )


@pytest.fixture
def sample_vendor() -> Vendor:
    """Create a sample vendor"""
    return Vendor(
        id="VENDOR-001",
        name="Premium Electronics Nigeria",
        email="vendor@example.ng",
        status=VendorStatus.ACTIVE,
        commission_rate=15.0,
        total_sales=5000000.00,
        rating=4.8,
        description="Leading electronics retailer in Nigeria"
    )


@pytest.fixture
def sample_product() -> Product:
    """Create a sample product"""
    return Product(
        id="PROD-001",
        sku="SKU-001",
        name="Wireless Headphones",
        description="High-quality wireless headphones with noise cancellation",
        category="Electronics",
        price=25000.00,
        cost=15000.00,
        status=ProductStatus.ACTIVE,
        vendor_id="VENDOR-001",
        rating=4.5,
        reviews_count=150
    )


@pytest.fixture
def sample_listing(sample_product, sample_vendor) -> Listing:
    """Create a sample listing"""
    return Listing(
        id="LIST-001",
        product_id=sample_product.id,
        vendor_id=sample_vendor.id,
        marketplace_type=MarketplaceType.MVM,
        quantity_available=100,
        price=25000.00,
        status=ProductStatus.ACTIVE
    )


@pytest.fixture
def nigeria_context() -> Dict[str, Any]:
    """Create Nigeria-specific context for INV-007 testing"""
    return {
        "country": "Nigeria",
        "currency": "NGN",
        "timezone": "Africa/Lagos",
        "locale": "en_NG",
        "tax_rate": 7.5,  # VAT rate in Nigeria
        "payment_gateways": ["paystack", "flutterwave", "interswitch"],
        "delivery_zones": ["Lagos", "Abuja", "Port Harcourt", "Kano", "Ibadan"]
    }
