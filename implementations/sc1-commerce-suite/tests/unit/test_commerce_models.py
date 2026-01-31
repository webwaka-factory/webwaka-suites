"""
Unit Tests for SC-1 Commerce Models

Tests for Order, OrderItem, Transaction, and related models.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.models.commerce import (
    Order, OrderItem, OrderStatus, Transaction, TransactionStatus,
    CreateOrderRequest, UpdateOrderRequest, CreateTransactionRequest,
    OrderResponse, TransactionResponse
)


class TestOrderItem:
    """Tests for OrderItem model"""

    def test_create_order_item(self):
        """Test creating a valid order item"""
        item = OrderItem(
            product_id="PROD-001",
            quantity=2,
            unit_price=29.99,
            total_price=59.98,
            sku="SKU-001"
        )
        
        assert item.product_id == "PROD-001"
        assert item.quantity == 2
        assert item.unit_price == 29.99
        assert item.total_price == 59.98
        assert item.sku == "SKU-001"

    def test_order_item_without_sku(self):
        """Test creating order item without optional SKU"""
        item = OrderItem(
            product_id="PROD-001",
            quantity=1,
            unit_price=10.00,
            total_price=10.00
        )
        
        assert item.sku is None

    def test_order_item_validation_required_fields(self):
        """Test that required fields are validated"""
        with pytest.raises(ValidationError):
            OrderItem(
                quantity=1,
                unit_price=10.00,
                total_price=10.00
            )


class TestOrderStatus:
    """Tests for OrderStatus enum"""

    def test_order_status_values(self):
        """Test all order status values exist"""
        assert OrderStatus.PENDING == "pending"
        assert OrderStatus.CONFIRMED == "confirmed"
        assert OrderStatus.PROCESSING == "processing"
        assert OrderStatus.SHIPPED == "shipped"
        assert OrderStatus.DELIVERED == "delivered"
        assert OrderStatus.CANCELLED == "cancelled"
        assert OrderStatus.RETURNED == "returned"

    def test_order_status_from_string(self):
        """Test creating status from string value"""
        status = OrderStatus("pending")
        assert status == OrderStatus.PENDING


class TestOrder:
    """Tests for Order model"""

    def test_create_order(self, sample_order_item, sample_shipping_address, sample_billing_address):
        """Test creating a valid order"""
        order = Order(
            id="ORD-001",
            customer_id="CUST-001",
            items=[sample_order_item],
            subtotal=59.98,
            tax=4.80,
            shipping=10.00,
            total=74.78,
            shipping_address=sample_shipping_address,
            billing_address=sample_billing_address
        )
        
        assert order.id == "ORD-001"
        assert order.customer_id == "CUST-001"
        assert len(order.items) == 1
        assert order.status == OrderStatus.PENDING  # Default
        assert order.total == 74.78

    def test_order_default_status(self, sample_order):
        """Test that order has default pending status"""
        assert sample_order.status == OrderStatus.PENDING

    def test_order_timestamps(self, sample_order):
        """Test that order has timestamps"""
        assert sample_order.created_at is not None
        assert sample_order.updated_at is not None
        assert isinstance(sample_order.created_at, datetime)

    def test_order_with_notes(self, sample_order_item, sample_shipping_address, sample_billing_address):
        """Test creating order with notes"""
        order = Order(
            id="ORD-002",
            customer_id="CUST-001",
            items=[sample_order_item],
            subtotal=59.98,
            total=59.98,
            shipping_address=sample_shipping_address,
            billing_address=sample_billing_address,
            notes="Please deliver before noon"
        )
        
        assert order.notes == "Please deliver before noon"

    def test_order_status_transition(self, sample_order):
        """Test order status can be changed"""
        sample_order.status = OrderStatus.CONFIRMED
        assert sample_order.status == OrderStatus.CONFIRMED
        
        sample_order.status = OrderStatus.SHIPPED
        assert sample_order.status == OrderStatus.SHIPPED

    def test_order_json_serialization(self, sample_order):
        """Test order can be serialized to JSON"""
        json_data = sample_order.model_dump_json()
        assert "ORD-001" in json_data
        assert "CUST-001" in json_data


class TestTransactionStatus:
    """Tests for TransactionStatus enum"""

    def test_transaction_status_values(self):
        """Test all transaction status values exist"""
        assert TransactionStatus.INITIATED == "initiated"
        assert TransactionStatus.PENDING == "pending"
        assert TransactionStatus.COMPLETED == "completed"
        assert TransactionStatus.FAILED == "failed"
        assert TransactionStatus.REFUNDED == "refunded"


class TestTransaction:
    """Tests for Transaction model"""

    def test_create_transaction(self):
        """Test creating a valid transaction"""
        transaction = Transaction(
            id="TXN-001",
            order_id="ORD-001",
            customer_id="CUST-001",
            amount=74.78,
            payment_method="card",
            payment_gateway="paystack"
        )
        
        assert transaction.id == "TXN-001"
        assert transaction.order_id == "ORD-001"
        assert transaction.amount == 74.78
        assert transaction.status == TransactionStatus.INITIATED

    def test_transaction_default_currency(self):
        """Test transaction has default USD currency"""
        transaction = Transaction(
            id="TXN-001",
            order_id="ORD-001",
            customer_id="CUST-001",
            amount=100.00,
            payment_method="card",
            payment_gateway="stripe"
        )
        
        assert transaction.currency == "USD"

    def test_transaction_with_ngn_currency(self):
        """Test transaction with Nigerian Naira (INV-007)"""
        transaction = Transaction(
            id="TXN-001",
            order_id="ORD-001",
            customer_id="CUST-001",
            amount=50000.00,
            currency="NGN",
            payment_method="card",
            payment_gateway="paystack"
        )
        
        assert transaction.currency == "NGN"

    def test_transaction_with_reference(self):
        """Test transaction with payment reference"""
        transaction = Transaction(
            id="TXN-001",
            order_id="ORD-001",
            customer_id="CUST-001",
            amount=100.00,
            payment_method="card",
            payment_gateway="paystack",
            reference_id="PAY_ref_123456"
        )
        
        assert transaction.reference_id == "PAY_ref_123456"

    def test_transaction_failed_with_error(self):
        """Test failed transaction with error message"""
        transaction = Transaction(
            id="TXN-001",
            order_id="ORD-001",
            customer_id="CUST-001",
            amount=100.00,
            payment_method="card",
            payment_gateway="paystack",
            status=TransactionStatus.FAILED,
            error_message="Insufficient funds"
        )
        
        assert transaction.status == TransactionStatus.FAILED
        assert transaction.error_message == "Insufficient funds"


class TestCreateOrderRequest:
    """Tests for CreateOrderRequest model"""

    def test_create_order_request(self, sample_order_item, sample_shipping_address, sample_billing_address):
        """Test creating an order request"""
        request = CreateOrderRequest(
            customer_id="CUST-001",
            items=[sample_order_item],
            shipping_address=sample_shipping_address,
            billing_address=sample_billing_address
        )
        
        assert request.customer_id == "CUST-001"
        assert len(request.items) == 1

    def test_create_order_request_with_notes(self, sample_order_item, sample_shipping_address, sample_billing_address):
        """Test creating order request with notes"""
        request = CreateOrderRequest(
            customer_id="CUST-001",
            items=[sample_order_item],
            shipping_address=sample_shipping_address,
            billing_address=sample_billing_address,
            notes="Gift wrap please"
        )
        
        assert request.notes == "Gift wrap please"


class TestUpdateOrderRequest:
    """Tests for UpdateOrderRequest model"""

    def test_update_order_status(self):
        """Test updating order status"""
        request = UpdateOrderRequest(status=OrderStatus.CONFIRMED)
        assert request.status == OrderStatus.CONFIRMED

    def test_update_order_notes(self):
        """Test updating order notes"""
        request = UpdateOrderRequest(notes="Updated delivery instructions")
        assert request.notes == "Updated delivery instructions"

    def test_update_order_partial(self):
        """Test partial update with only status"""
        request = UpdateOrderRequest(status=OrderStatus.SHIPPED)
        assert request.status == OrderStatus.SHIPPED
        assert request.notes is None


class TestCreateTransactionRequest:
    """Tests for CreateTransactionRequest model"""

    def test_create_transaction_request(self):
        """Test creating a transaction request"""
        request = CreateTransactionRequest(
            order_id="ORD-001",
            customer_id="CUST-001",
            amount=100.00,
            payment_method="card",
            payment_gateway="paystack"
        )
        
        assert request.order_id == "ORD-001"
        assert request.amount == 100.00
        assert request.payment_gateway == "paystack"


class TestOrderResponse:
    """Tests for OrderResponse model"""

    def test_successful_order_response(self, sample_order):
        """Test successful order response"""
        response = OrderResponse(
            success=True,
            message="Order created successfully",
            data=sample_order
        )
        
        assert response.success is True
        assert response.data is not None
        assert response.data.id == "ORD-001"

    def test_failed_order_response(self):
        """Test failed order response"""
        response = OrderResponse(
            success=False,
            message="Failed to create order"
        )
        
        assert response.success is False
        assert response.data is None


class TestTransactionResponse:
    """Tests for TransactionResponse model"""

    def test_successful_transaction_response(self, sample_transaction):
        """Test successful transaction response"""
        response = TransactionResponse(
            success=True,
            message="Transaction completed",
            data=sample_transaction
        )
        
        assert response.success is True
        assert response.data is not None

    def test_failed_transaction_response(self):
        """Test failed transaction response"""
        response = TransactionResponse(
            success=False,
            message="Payment failed"
        )
        
        assert response.success is False
        assert response.data is None
