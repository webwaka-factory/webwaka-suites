"""
Integration Tests for SC-1 Commerce Suite API Endpoints

Tests for all API endpoints including orders, marketplace, inventory, and more.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Tests for health and root endpoints"""

    def test_health_check(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "SC-1 Commerce Suite V1"
        assert data["version"] == "1.0.0"

    def test_root_endpoint(self, test_client):
        """Test root endpoint"""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "Welcome to SC-1 Commerce Suite V1" in data["message"]
        assert data["documentation"] == "/docs"


class TestDashboardEndpoints:
    """Tests for dashboard endpoints"""

    def test_get_dashboard(self, test_client):
        """Test get dashboard data"""
        response = test_client.get("/api/v1/dashboard")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_orders" in data["data"]
        assert "total_revenue" in data["data"]
        assert "active_customers" in data["data"]
        assert "pending_shipments" in data["data"]


class TestOrderEndpoints:
    """Tests for order endpoints"""

    def test_list_orders(self, test_client):
        """Test list orders endpoint"""
        response = test_client.get("/api/v1/orders")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_create_order(self, test_client, sample_shipping_address, sample_billing_address):
        """Test create order endpoint"""
        order_data = {
            "customer_id": "CUST-001",
            "items": [
                {
                    "product_id": "PROD-001",
                    "quantity": 2,
                    "unit_price": 29.99,
                    "total_price": 59.98
                }
            ],
            "shipping_address": sample_shipping_address,
            "billing_address": sample_billing_address
        }
        
        response = test_client.post("/api/v1/orders", json=order_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Order created successfully"

    def test_get_order(self, test_client):
        """Test get order by ID endpoint"""
        response = test_client.get("/api/v1/orders/ORD-001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "ORD-001"

    def test_create_order_nigeria_address(self, test_client):
        """Test create order with Nigeria address (INV-007)"""
        order_data = {
            "customer_id": "CUST-NG-001",
            "items": [
                {
                    "product_id": "PROD-001",
                    "quantity": 1,
                    "unit_price": 25000.00,
                    "total_price": 25000.00
                }
            ],
            "shipping_address": {
                "street": "123 Victoria Island",
                "city": "Lagos",
                "state": "Lagos",
                "country": "Nigeria",
                "postal_code": "100001"
            },
            "billing_address": {
                "street": "123 Victoria Island",
                "city": "Lagos",
                "state": "Lagos",
                "country": "Nigeria",
                "postal_code": "100001"
            }
        }
        
        response = test_client.post("/api/v1/orders", json=order_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestMarketplaceEndpoints:
    """Tests for marketplace endpoints"""

    def test_list_products(self, test_client):
        """Test list products endpoint"""
        response = test_client.get("/api/v1/marketplace/products")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    def test_create_product(self, test_client):
        """Test create product endpoint"""
        product_data = {
            "sku": "SKU-NEW-001",
            "name": "New Product",
            "description": "A new test product",
            "category": "Electronics",
            "price": 99.99
        }
        
        response = test_client.post("/api/v1/marketplace/products", json=product_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Product created successfully"

    def test_list_vendors(self, test_client):
        """Test list vendors endpoint"""
        response = test_client.get("/api/v1/marketplace/vendors")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    def test_create_product_mvm(self, test_client):
        """Test create product for MVM with vendor"""
        product_data = {
            "sku": "SKU-MVM-001",
            "name": "Vendor Product",
            "description": "Product from a vendor",
            "category": "Fashion",
            "price": 75.00,
            "vendor_id": "VENDOR-001"
        }
        
        response = test_client.post("/api/v1/marketplace/products", json=product_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestInventoryEndpoints:
    """Tests for inventory endpoints"""

    def test_list_inventory(self, test_client):
        """Test list inventory endpoint"""
        response = test_client.get("/api/v1/inventory")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    def test_sync_inventory(self, test_client):
        """Test inventory sync endpoint"""
        response = test_client.post("/api/v1/inventory/sync")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "sync_id" in data["data"]
        assert data["data"]["status"] == "pending"


class TestPOSEndpoints:
    """Tests for POS endpoints"""

    def test_create_pos_transaction(self, test_client):
        """Test create POS transaction endpoint"""
        transaction_data = {
            "order_id": "ORD-POS-001",
            "customer_id": "CUST-001",
            "amount": 150.00,
            "payment_method": "card",
            "terminal_id": "TERM-001"
        }
        
        response = test_client.post("/api/v1/pos/transactions", json=transaction_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "POS transaction created successfully"

    def test_create_pos_transaction_nigeria(self, test_client):
        """Test POS transaction with Nigeria payment (INV-007)"""
        transaction_data = {
            "order_id": "ORD-POS-NG-001",
            "customer_id": "CUST-NG-001",
            "amount": 50000.00,
            "currency": "NGN",
            "payment_method": "card",
            "payment_gateway": "paystack",
            "terminal_id": "TERM-LAGOS-001"
        }
        
        response = test_client.post("/api/v1/pos/transactions", json=transaction_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestLogisticsEndpoints:
    """Tests for logistics endpoints"""

    def test_list_shipments(self, test_client):
        """Test list shipments endpoint"""
        response = test_client.get("/api/v1/logistics/shipments")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    def test_create_shipment(self, test_client):
        """Test create shipment endpoint"""
        shipment_data = {
            "order_id": "ORD-001",
            "carrier": "DHL",
            "tracking_number": "DHL123456789",
            "destination": {
                "city": "Lagos",
                "country": "Nigeria"
            }
        }
        
        response = test_client.post("/api/v1/logistics/shipments", json=shipment_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Shipment created successfully"


class TestAccountingEndpoints:
    """Tests for accounting endpoints"""

    def test_list_invoices(self, test_client):
        """Test list invoices endpoint"""
        response = test_client.get("/api/v1/accounting/invoices")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    def test_create_invoice(self, test_client):
        """Test create invoice endpoint"""
        invoice_data = {
            "order_id": "ORD-001",
            "customer_id": "CUST-001",
            "amount": 74.78,
            "currency": "NGN",
            "due_date": "2024-02-15"
        }
        
        response = test_client.post("/api/v1/accounting/invoices", json=invoice_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Invoice created successfully"


class TestEngagementEndpoints:
    """Tests for customer engagement endpoints"""

    def test_list_loyalty_programs(self, test_client):
        """Test list loyalty programs endpoint"""
        response = test_client.get("/api/v1/engagement/loyalty")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_create_loyalty_program(self, test_client):
        """Test create loyalty program endpoint"""
        loyalty_data = {
            "name": "Premium Rewards",
            "points_per_naira": 1,
            "minimum_points_redemption": 1000
        }
        
        response = test_client.post("/api/v1/engagement/loyalty", json=loyalty_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_list_coupons(self, test_client):
        """Test list coupons endpoint"""
        response = test_client.get("/api/v1/engagement/coupons")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_create_coupon(self, test_client):
        """Test create coupon endpoint"""
        coupon_data = {
            "code": "SAVE20",
            "discount_type": "percentage",
            "discount_value": 20,
            "valid_until": "2024-12-31"
        }
        
        response = test_client.post("/api/v1/engagement/coupons", json=coupon_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_list_subscriptions(self, test_client):
        """Test list subscriptions endpoint"""
        response = test_client.get("/api/v1/engagement/subscriptions")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_create_subscription(self, test_client):
        """Test create subscription endpoint"""
        subscription_data = {
            "customer_id": "CUST-001",
            "plan": "monthly",
            "amount": 5000.00,
            "currency": "NGN"
        }
        
        response = test_client.post("/api/v1/engagement/subscriptions", json=subscription_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_list_refunds(self, test_client):
        """Test list refunds endpoint"""
        response = test_client.get("/api/v1/engagement/refunds")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_create_refund(self, test_client):
        """Test create refund endpoint"""
        refund_data = {
            "order_id": "ORD-001",
            "transaction_id": "TXN-001",
            "amount": 74.78,
            "reason": "Customer request"
        }
        
        response = test_client.post("/api/v1/engagement/refunds", json=refund_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestAPIDocumentation:
    """Tests for API documentation endpoints"""

    def test_openapi_json(self, test_client):
        """Test OpenAPI JSON endpoint"""
        response = test_client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "SC-1 Commerce Suite V1"

    def test_docs_endpoint(self, test_client):
        """Test Swagger docs endpoint"""
        response = test_client.get("/docs")
        
        assert response.status_code == 200

    def test_redoc_endpoint(self, test_client):
        """Test ReDoc endpoint"""
        response = test_client.get("/redoc")
        
        assert response.status_code == 200
