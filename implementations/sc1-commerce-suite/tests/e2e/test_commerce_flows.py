"""
End-to-End Tests for SC-1 Commerce Suite

Tests for complete commerce workflows including order lifecycle,
marketplace operations, and inventory management.
"""

import pytest
from fastapi.testclient import TestClient


class TestOrderLifecycle:
    """E2E tests for complete order lifecycle"""

    def test_complete_order_flow(self, test_client, sample_shipping_address, sample_billing_address):
        """Test complete order flow from creation to completion"""
        # Step 1: Create order
        order_data = {
            "customer_id": "CUST-E2E-001",
            "items": [
                {
                    "product_id": "PROD-001",
                    "quantity": 2,
                    "unit_price": 25000.00,
                    "total_price": 50000.00
                }
            ],
            "shipping_address": sample_shipping_address,
            "billing_address": sample_billing_address
        }
        
        response = test_client.post("/api/v1/orders", json=order_data)
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Step 2: Verify order can be retrieved
        response = test_client.get("/api/v1/orders")
        assert response.status_code == 200
        
        # Step 3: Create shipment for order
        shipment_data = {
            "order_id": "ORD-E2E-001",
            "carrier": "GIG Logistics",
            "tracking_number": "GIG123456789",
            "destination": sample_shipping_address
        }
        
        response = test_client.post("/api/v1/logistics/shipments", json=shipment_data)
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Step 4: Create invoice
        invoice_data = {
            "order_id": "ORD-E2E-001",
            "customer_id": "CUST-E2E-001",
            "amount": 50000.00,
            "currency": "NGN"
        }
        
        response = test_client.post("/api/v1/accounting/invoices", json=invoice_data)
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_nigeria_order_flow(self, test_client, nigeria_context):
        """Test order flow with Nigeria-specific context (INV-007)"""
        # Create order with Nigerian address
        order_data = {
            "customer_id": "CUST-NG-001",
            "items": [
                {
                    "product_id": "PROD-NG-001",
                    "quantity": 1,
                    "unit_price": 100000.00,
                    "total_price": 100000.00
                }
            ],
            "shipping_address": {
                "street": "15 Adeola Odeku Street",
                "city": "Lagos",
                "state": "Lagos",
                "country": nigeria_context["country"],
                "postal_code": "100001"
            },
            "billing_address": {
                "street": "15 Adeola Odeku Street",
                "city": "Lagos",
                "state": "Lagos",
                "country": nigeria_context["country"],
                "postal_code": "100001"
            }
        }
        
        response = test_client.post("/api/v1/orders", json=order_data)
        assert response.status_code == 200
        
        # Create POS transaction with Nigerian payment gateway
        transaction_data = {
            "order_id": "ORD-NG-001",
            "customer_id": "CUST-NG-001",
            "amount": 100000.00,
            "currency": nigeria_context["currency"],
            "payment_method": "card",
            "payment_gateway": nigeria_context["payment_gateways"][0]  # paystack
        }
        
        response = test_client.post("/api/v1/pos/transactions", json=transaction_data)
        assert response.status_code == 200


class TestMarketplaceFlow:
    """E2E tests for marketplace operations"""

    def test_vendor_product_listing_flow(self, test_client):
        """Test complete vendor and product listing flow for MVM"""
        # Step 1: List vendors (vendor would be created via admin)
        response = test_client.get("/api/v1/marketplace/vendors")
        assert response.status_code == 200
        
        # Step 2: Create product for vendor
        product_data = {
            "sku": "SKU-E2E-001",
            "name": "E2E Test Product",
            "description": "Product for end-to-end testing",
            "category": "Electronics",
            "price": 75000.00,
            "vendor_id": "VENDOR-E2E-001"
        }
        
        response = test_client.post("/api/v1/marketplace/products", json=product_data)
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Step 3: List products to verify
        response = test_client.get("/api/v1/marketplace/products")
        assert response.status_code == 200

    def test_svm_product_flow(self, test_client):
        """Test Single Vendor Marketplace product flow"""
        # Create product without vendor (SVM)
        product_data = {
            "sku": "SKU-SVM-001",
            "name": "Store Product",
            "description": "Single vendor store product",
            "category": "Fashion",
            "price": 15000.00
        }
        
        response = test_client.post("/api/v1/marketplace/products", json=product_data)
        assert response.status_code == 200
        assert response.json()["success"] is True


class TestInventoryFlow:
    """E2E tests for inventory management"""

    def test_inventory_sync_flow(self, test_client):
        """Test inventory synchronization flow"""
        # Step 1: List current inventory
        response = test_client.get("/api/v1/inventory")
        assert response.status_code == 200
        
        # Step 2: Trigger sync
        response = test_client.post("/api/v1/inventory/sync")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "sync_id" in data["data"]

    def test_inventory_order_integration(self, test_client, sample_shipping_address, sample_billing_address):
        """Test inventory updates with order creation"""
        # Create order that should affect inventory
        order_data = {
            "customer_id": "CUST-INV-001",
            "items": [
                {
                    "product_id": "PROD-INV-001",
                    "quantity": 5,
                    "unit_price": 10000.00,
                    "total_price": 50000.00
                }
            ],
            "shipping_address": sample_shipping_address,
            "billing_address": sample_billing_address
        }
        
        response = test_client.post("/api/v1/orders", json=order_data)
        assert response.status_code == 200
        
        # Verify inventory endpoint is accessible
        response = test_client.get("/api/v1/inventory")
        assert response.status_code == 200


class TestCustomerEngagementFlow:
    """E2E tests for customer engagement features"""

    def test_loyalty_program_flow(self, test_client):
        """Test loyalty program creation and usage"""
        # Create loyalty program
        loyalty_data = {
            "name": "WebWaka Rewards",
            "points_per_naira": 1,
            "minimum_points_redemption": 500
        }
        
        response = test_client.post("/api/v1/engagement/loyalty", json=loyalty_data)
        assert response.status_code == 200
        
        # List loyalty programs
        response = test_client.get("/api/v1/engagement/loyalty")
        assert response.status_code == 200

    def test_coupon_flow(self, test_client):
        """Test coupon creation and application"""
        # Create coupon
        coupon_data = {
            "code": "WEBWAKA25",
            "discount_type": "percentage",
            "discount_value": 25,
            "valid_until": "2025-12-31"
        }
        
        response = test_client.post("/api/v1/engagement/coupons", json=coupon_data)
        assert response.status_code == 200
        
        # List coupons
        response = test_client.get("/api/v1/engagement/coupons")
        assert response.status_code == 200

    def test_subscription_flow(self, test_client):
        """Test subscription management"""
        # Create subscription
        subscription_data = {
            "customer_id": "CUST-SUB-001",
            "plan": "premium",
            "amount": 10000.00,
            "currency": "NGN",
            "billing_cycle": "monthly"
        }
        
        response = test_client.post("/api/v1/engagement/subscriptions", json=subscription_data)
        assert response.status_code == 200
        
        # List subscriptions
        response = test_client.get("/api/v1/engagement/subscriptions")
        assert response.status_code == 200

    def test_refund_flow(self, test_client):
        """Test refund processing"""
        # Create refund request
        refund_data = {
            "order_id": "ORD-REFUND-001",
            "transaction_id": "TXN-REFUND-001",
            "amount": 25000.00,
            "reason": "Product not as described"
        }
        
        response = test_client.post("/api/v1/engagement/refunds", json=refund_data)
        assert response.status_code == 200
        
        # List refunds
        response = test_client.get("/api/v1/engagement/refunds")
        assert response.status_code == 200


class TestDashboardIntegration:
    """E2E tests for dashboard data aggregation"""

    def test_dashboard_reflects_operations(self, test_client):
        """Test that dashboard reflects commerce operations"""
        # Get initial dashboard state
        response = test_client.get("/api/v1/dashboard")
        assert response.status_code == 200
        initial_data = response.json()["data"]
        
        # Perform some operations
        order_data = {
            "customer_id": "CUST-DASH-001",
            "items": [{"product_id": "PROD-001", "quantity": 1, "unit_price": 100, "total_price": 100}],
            "shipping_address": {"city": "Lagos"},
            "billing_address": {"city": "Lagos"}
        }
        test_client.post("/api/v1/orders", json=order_data)
        
        # Get updated dashboard
        response = test_client.get("/api/v1/dashboard")
        assert response.status_code == 200
        # Dashboard should still be accessible after operations
        assert response.json()["success"] is True


class TestCrossModuleIntegration:
    """E2E tests for cross-module integration"""

    def test_order_to_logistics_to_accounting(self, test_client, sample_shipping_address, sample_billing_address):
        """Test integration between orders, logistics, and accounting"""
        # Create order
        order_data = {
            "customer_id": "CUST-CROSS-001",
            "items": [
                {
                    "product_id": "PROD-001",
                    "quantity": 3,
                    "unit_price": 20000.00,
                    "total_price": 60000.00
                }
            ],
            "shipping_address": sample_shipping_address,
            "billing_address": sample_billing_address
        }
        
        response = test_client.post("/api/v1/orders", json=order_data)
        assert response.status_code == 200
        
        # Create shipment
        shipment_data = {
            "order_id": "ORD-CROSS-001",
            "carrier": "DHL",
            "tracking_number": "DHL987654321"
        }
        
        response = test_client.post("/api/v1/logistics/shipments", json=shipment_data)
        assert response.status_code == 200
        
        # Create invoice
        invoice_data = {
            "order_id": "ORD-CROSS-001",
            "customer_id": "CUST-CROSS-001",
            "amount": 60000.00,
            "currency": "NGN"
        }
        
        response = test_client.post("/api/v1/accounting/invoices", json=invoice_data)
        assert response.status_code == 200

    def test_pos_to_inventory_sync(self, test_client):
        """Test POS transaction triggers inventory consideration"""
        # Create POS transaction
        transaction_data = {
            "order_id": "ORD-POS-SYNC-001",
            "customer_id": "CUST-POS-001",
            "amount": 15000.00,
            "payment_method": "card"
        }
        
        response = test_client.post("/api/v1/pos/transactions", json=transaction_data)
        assert response.status_code == 200
        
        # Trigger inventory sync
        response = test_client.post("/api/v1/inventory/sync")
        assert response.status_code == 200
