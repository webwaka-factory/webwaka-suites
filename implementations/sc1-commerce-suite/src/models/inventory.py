"""
Inventory Models

Data models for inventory management and synchronization.
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SyncStatus(str, Enum):
    """Inventory sync status enumeration"""
    PENDING = "pending"
    SYNCING = "syncing"
    COMPLETED = "completed"
    FAILED = "failed"


class SyncTarget(str, Enum):
    """Inventory sync target enumeration"""
    POS = "pos"
    SVM = "svm"
    MVM = "mvm"


class InventoryItem(BaseModel):
    """Inventory item model"""
    id: str = Field(..., description="Unique inventory item ID")
    product_id: str = Field(..., description="Product ID")
    sku: str = Field(..., description="Stock Keeping Unit")
    location: str = Field(..., description="Storage location")
    quantity_on_hand: int = Field(..., description="Current quantity on hand")
    quantity_reserved: int = Field(default=0, description="Reserved quantity")
    quantity_available: int = Field(..., description="Available quantity")
    reorder_point: int = Field(default=10, description="Reorder point")
    reorder_quantity: int = Field(default=50, description="Reorder quantity")
    last_counted: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "INV-001",
                "product_id": "PROD-001",
                "sku": "SKU-001",
                "location": "Warehouse A",
                "quantity_on_hand": 100,
                "quantity_reserved": 10,
                "quantity_available": 90,
                "reorder_point": 20,
                "reorder_quantity": 100
            }
        }


class StockLevel(BaseModel):
    """Stock level tracking model"""
    id: str = Field(..., description="Unique stock level ID")
    inventory_item_id: str = Field(..., description="Inventory item ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    quantity_on_hand: int = Field(..., description="Quantity on hand at this time")
    quantity_reserved: int = Field(..., description="Quantity reserved at this time")
    quantity_available: int = Field(..., description="Quantity available at this time")
    change_reason: Optional[str] = None
    change_amount: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "STOCK-001",
                "inventory_item_id": "INV-001",
                "quantity_on_hand": 100,
                "quantity_reserved": 10,
                "quantity_available": 90,
                "change_reason": "Sale",
                "change_amount": -5
            }
        }


class InventorySyncConfig(BaseModel):
    """Inventory synchronization configuration"""
    id: str = Field(..., description="Unique sync config ID")
    enabled: bool = Field(default=False, description="Is sync enabled")
    sync_targets: List[SyncTarget] = Field(..., description="Targets to sync to")
    sync_frequency: str = Field(default="realtime", description="Sync frequency (realtime, hourly, daily)")
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "SYNC-001",
                "enabled": True,
                "sync_targets": ["pos", "svm", "mvm"],
                "sync_frequency": "realtime"
            }
        }


class InventorySyncEvent(BaseModel):
    """Inventory sync event model"""
    id: str = Field(..., description="Unique sync event ID")
    config_id: str = Field(..., description="Sync config ID")
    status: SyncStatus = Field(default=SyncStatus.PENDING)
    items_synced: int = Field(default=0)
    items_failed: int = Field(default=0)
    error_message: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "SYNC-EVT-001",
                "config_id": "SYNC-001",
                "status": "completed",
                "items_synced": 150,
                "items_failed": 0
            }
        }


class UpdateInventoryRequest(BaseModel):
    """Request model for updating inventory"""
    quantity_on_hand: Optional[int] = None
    quantity_reserved: Optional[int] = None
    reorder_point: Optional[int] = None
    reorder_quantity: Optional[int] = None


class CreateSyncConfigRequest(BaseModel):
    """Request model for creating sync config"""
    enabled: bool
    sync_targets: List[SyncTarget]
    sync_frequency: str = "realtime"


class InventoryResponse(BaseModel):
    """Response model for inventory operations"""
    success: bool
    message: str
    data: Optional[InventoryItem] = None


class SyncConfigResponse(BaseModel):
    """Response model for sync config operations"""
    success: bool
    message: str
    data: Optional[InventorySyncConfig] = None
