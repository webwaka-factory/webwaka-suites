"""
Unit Tests for SC-1 Inventory Models

Tests for InventoryItem, StockLevel, InventorySyncConfig, and related models.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.models.inventory import (
    InventoryItem, StockLevel, InventorySyncConfig, InventorySyncEvent,
    SyncStatus, SyncTarget, UpdateInventoryRequest, CreateSyncConfigRequest,
    InventoryResponse, SyncConfigResponse
)


class TestSyncStatus:
    """Tests for SyncStatus enum"""

    def test_sync_status_values(self):
        """Test all sync status values exist"""
        assert SyncStatus.PENDING == "pending"
        assert SyncStatus.SYNCING == "syncing"
        assert SyncStatus.COMPLETED == "completed"
        assert SyncStatus.FAILED == "failed"


class TestSyncTarget:
    """Tests for SyncTarget enum"""

    def test_sync_target_values(self):
        """Test all sync target values exist"""
        assert SyncTarget.POS == "pos"
        assert SyncTarget.SVM == "svm"
        assert SyncTarget.MVM == "mvm"


class TestInventoryItem:
    """Tests for InventoryItem model"""

    def test_create_inventory_item(self):
        """Test creating a valid inventory item"""
        item = InventoryItem(
            id="INV-001",
            product_id="PROD-001",
            sku="SKU-001",
            location="Warehouse Lagos",
            quantity_on_hand=100,
            quantity_reserved=10,
            quantity_available=90
        )
        
        assert item.id == "INV-001"
        assert item.product_id == "PROD-001"
        assert item.quantity_on_hand == 100
        assert item.quantity_available == 90

    def test_inventory_item_default_values(self):
        """Test inventory item default values"""
        item = InventoryItem(
            id="INV-001",
            product_id="PROD-001",
            sku="SKU-001",
            location="Warehouse",
            quantity_on_hand=50,
            quantity_available=50
        )
        
        assert item.quantity_reserved == 0
        assert item.reorder_point == 10
        assert item.reorder_quantity == 50

    def test_inventory_item_timestamps(self, sample_inventory_item):
        """Test inventory item has timestamps"""
        assert sample_inventory_item.created_at is not None
        assert sample_inventory_item.updated_at is not None
        assert isinstance(sample_inventory_item.created_at, datetime)

    def test_inventory_item_with_last_counted(self):
        """Test inventory item with last counted date"""
        item = InventoryItem(
            id="INV-001",
            product_id="PROD-001",
            sku="SKU-001",
            location="Warehouse",
            quantity_on_hand=100,
            quantity_available=100,
            last_counted=datetime.utcnow()
        )
        
        assert item.last_counted is not None

    def test_inventory_item_nigeria_location(self):
        """Test inventory item with Nigeria location (INV-007)"""
        item = InventoryItem(
            id="INV-001",
            product_id="PROD-001",
            sku="SKU-001",
            location="Warehouse Lagos, Nigeria",
            quantity_on_hand=500,
            quantity_available=450,
            quantity_reserved=50
        )
        
        assert "Nigeria" in item.location
        assert "Lagos" in item.location

    def test_inventory_item_json_serialization(self, sample_inventory_item):
        """Test inventory item can be serialized to JSON"""
        json_data = sample_inventory_item.model_dump_json()
        assert "INV-001" in json_data
        assert "PROD-001" in json_data


class TestStockLevel:
    """Tests for StockLevel model"""

    def test_create_stock_level(self):
        """Test creating a stock level record"""
        stock = StockLevel(
            id="STOCK-001",
            inventory_item_id="INV-001",
            quantity_on_hand=100,
            quantity_reserved=10,
            quantity_available=90
        )
        
        assert stock.id == "STOCK-001"
        assert stock.inventory_item_id == "INV-001"
        assert stock.quantity_on_hand == 100

    def test_stock_level_with_change(self):
        """Test stock level with change tracking"""
        stock = StockLevel(
            id="STOCK-001",
            inventory_item_id="INV-001",
            quantity_on_hand=95,
            quantity_reserved=10,
            quantity_available=85,
            change_reason="Sale",
            change_amount=-5
        )
        
        assert stock.change_reason == "Sale"
        assert stock.change_amount == -5

    def test_stock_level_timestamp(self):
        """Test stock level has timestamp"""
        stock = StockLevel(
            id="STOCK-001",
            inventory_item_id="INV-001",
            quantity_on_hand=100,
            quantity_reserved=0,
            quantity_available=100
        )
        
        assert stock.timestamp is not None
        assert isinstance(stock.timestamp, datetime)


class TestInventorySyncConfig:
    """Tests for InventorySyncConfig model"""

    def test_create_sync_config(self):
        """Test creating a sync configuration"""
        config = InventorySyncConfig(
            id="SYNC-001",
            enabled=True,
            sync_targets=[SyncTarget.POS, SyncTarget.SVM]
        )
        
        assert config.id == "SYNC-001"
        assert config.enabled is True
        assert len(config.sync_targets) == 2

    def test_sync_config_default_frequency(self):
        """Test sync config default frequency"""
        config = InventorySyncConfig(
            id="SYNC-001",
            enabled=True,
            sync_targets=[SyncTarget.POS]
        )
        
        assert config.sync_frequency == "realtime"

    def test_sync_config_all_targets(self, sample_sync_config):
        """Test sync config with all targets"""
        assert SyncTarget.POS in sample_sync_config.sync_targets
        assert SyncTarget.SVM in sample_sync_config.sync_targets
        assert SyncTarget.MVM in sample_sync_config.sync_targets

    def test_sync_config_disabled(self):
        """Test disabled sync config"""
        config = InventorySyncConfig(
            id="SYNC-001",
            enabled=False,
            sync_targets=[SyncTarget.POS]
        )
        
        assert config.enabled is False

    def test_sync_config_timestamps(self, sample_sync_config):
        """Test sync config has timestamps"""
        assert sample_sync_config.created_at is not None
        assert sample_sync_config.updated_at is not None


class TestInventorySyncEvent:
    """Tests for InventorySyncEvent model"""

    def test_create_sync_event(self):
        """Test creating a sync event"""
        event = InventorySyncEvent(
            id="SYNC-EVT-001",
            config_id="SYNC-001"
        )
        
        assert event.id == "SYNC-EVT-001"
        assert event.config_id == "SYNC-001"
        assert event.status == SyncStatus.PENDING

    def test_sync_event_completed(self):
        """Test completed sync event"""
        event = InventorySyncEvent(
            id="SYNC-EVT-001",
            config_id="SYNC-001",
            status=SyncStatus.COMPLETED,
            items_synced=150,
            items_failed=0,
            completed_at=datetime.utcnow()
        )
        
        assert event.status == SyncStatus.COMPLETED
        assert event.items_synced == 150
        assert event.items_failed == 0
        assert event.completed_at is not None

    def test_sync_event_failed(self):
        """Test failed sync event"""
        event = InventorySyncEvent(
            id="SYNC-EVT-001",
            config_id="SYNC-001",
            status=SyncStatus.FAILED,
            items_synced=50,
            items_failed=100,
            error_message="Connection timeout"
        )
        
        assert event.status == SyncStatus.FAILED
        assert event.items_failed == 100
        assert event.error_message == "Connection timeout"

    def test_sync_event_in_progress(self):
        """Test sync event in progress"""
        event = InventorySyncEvent(
            id="SYNC-EVT-001",
            config_id="SYNC-001",
            status=SyncStatus.SYNCING,
            items_synced=75
        )
        
        assert event.status == SyncStatus.SYNCING
        assert event.completed_at is None


class TestUpdateInventoryRequest:
    """Tests for UpdateInventoryRequest model"""

    def test_update_quantity_on_hand(self):
        """Test updating quantity on hand"""
        request = UpdateInventoryRequest(quantity_on_hand=150)
        assert request.quantity_on_hand == 150

    def test_update_quantity_reserved(self):
        """Test updating quantity reserved"""
        request = UpdateInventoryRequest(quantity_reserved=20)
        assert request.quantity_reserved == 20

    def test_update_reorder_settings(self):
        """Test updating reorder settings"""
        request = UpdateInventoryRequest(
            reorder_point=30,
            reorder_quantity=200
        )
        
        assert request.reorder_point == 30
        assert request.reorder_quantity == 200

    def test_partial_update(self):
        """Test partial update"""
        request = UpdateInventoryRequest(quantity_on_hand=100)
        
        assert request.quantity_on_hand == 100
        assert request.quantity_reserved is None
        assert request.reorder_point is None


class TestCreateSyncConfigRequest:
    """Tests for CreateSyncConfigRequest model"""

    def test_create_sync_config_request(self):
        """Test creating sync config request"""
        request = CreateSyncConfigRequest(
            enabled=True,
            sync_targets=[SyncTarget.POS, SyncTarget.SVM]
        )
        
        assert request.enabled is True
        assert len(request.sync_targets) == 2

    def test_sync_config_request_default_frequency(self):
        """Test sync config request default frequency"""
        request = CreateSyncConfigRequest(
            enabled=True,
            sync_targets=[SyncTarget.MVM]
        )
        
        assert request.sync_frequency == "realtime"

    def test_sync_config_request_custom_frequency(self):
        """Test sync config request with custom frequency"""
        request = CreateSyncConfigRequest(
            enabled=True,
            sync_targets=[SyncTarget.POS],
            sync_frequency="hourly"
        )
        
        assert request.sync_frequency == "hourly"


class TestInventoryResponse:
    """Tests for InventoryResponse model"""

    def test_successful_inventory_response(self, sample_inventory_item):
        """Test successful inventory response"""
        response = InventoryResponse(
            success=True,
            message="Inventory item retrieved",
            data=sample_inventory_item
        )
        
        assert response.success is True
        assert response.data is not None
        assert response.data.id == "INV-001"

    def test_failed_inventory_response(self):
        """Test failed inventory response"""
        response = InventoryResponse(
            success=False,
            message="Inventory item not found"
        )
        
        assert response.success is False
        assert response.data is None


class TestSyncConfigResponse:
    """Tests for SyncConfigResponse model"""

    def test_successful_sync_config_response(self, sample_sync_config):
        """Test successful sync config response"""
        response = SyncConfigResponse(
            success=True,
            message="Sync config created",
            data=sample_sync_config
        )
        
        assert response.success is True
        assert response.data is not None
        assert response.data.enabled is True

    def test_failed_sync_config_response(self):
        """Test failed sync config response"""
        response = SyncConfigResponse(
            success=False,
            message="Failed to create sync config"
        )
        
        assert response.success is False
        assert response.data is None
