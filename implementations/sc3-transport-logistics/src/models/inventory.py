"""
Inventory Models

Data models for inventory synchronization with offline-safe operations.
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SyncStatus(str, Enum):
    """Sync status enumeration"""
    PENDING = "pending"
    SYNCING = "syncing"
    COMPLETED = "completed"
    FAILED = "failed"
    OFFLINE = "offline"


class SyncTarget(str, Enum):
    """Sync target enumeration"""
    AGENT = "agent"
    PARK = "park"
    OPERATOR = "operator"


class ConflictResolutionStrategy(str, Enum):
    """Conflict resolution strategy enumeration"""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MANUAL = "manual"


class InventoryItem(BaseModel):
    """Inventory item model"""
    id: str = Field(..., description="Unique inventory item ID")
    route_id: str = Field(..., description="Route ID")
    schedule_id: str = Field(..., description="Schedule ID")
    total_seats: int = Field(..., description="Total seats")
    booked_seats: int = Field(default=0, description="Booked seats")
    available_seats: int = Field(..., description="Available seats")
    held_seats: int = Field(default=0, description="Held seats")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "INV-001",
                "route_id": "RT-001",
                "schedule_id": "SCH-001",
                "total_seats": 50,
                "booked_seats": 10,
                "available_seats": 40,
                "held_seats": 5
            }
        }


class InventorySyncConfig(BaseModel):
    """Inventory sync configuration"""
    id: str = Field(..., description="Unique sync config ID")
    enabled: bool = Field(default=False, description="Is sync enabled")
    sync_targets: List[SyncTarget] = Field(..., description="Targets to sync to")
    sync_frequency: str = Field(default="realtime", description="Sync frequency")
    offline_mode: bool = Field(default=True, description="Support offline mode")
    conflict_resolution: ConflictResolutionStrategy = Field(
        default=ConflictResolutionStrategy.LAST_WRITE_WINS
    )
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "SYNC-001",
                "enabled": True,
                "sync_targets": ["agent", "park", "operator"],
                "sync_frequency": "realtime",
                "offline_mode": True
            }
        }


class InventorySyncEvent(BaseModel):
    """Inventory sync event model"""
    id: str = Field(..., description="Unique sync event ID")
    config_id: str = Field(..., description="Sync config ID")
    status: SyncStatus = Field(default=SyncStatus.PENDING)
    items_synced: int = Field(default=0)
    items_failed: int = Field(default=0)
    items_conflicted: int = Field(default=0)
    error_message: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "SYNC-EVT-001",
                "config_id": "SYNC-001",
                "status": "completed",
                "items_synced": 100,
                "items_failed": 0,
                "items_conflicted": 0
            }
        }


class OfflineSyncQueue(BaseModel):
    """Offline sync queue model"""
    id: str = Field(..., description="Unique queue ID")
    target_id: str = Field(..., description="Target ID (agent, park, operator)")
    target_type: SyncTarget = Field(..., description="Target type")
    operation: str = Field(..., description="Operation (create, update, delete)")
    data: Dict[str, Any] = Field(..., description="Data to sync")
    status: SyncStatus = Field(default=SyncStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    synced_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "QUEUE-001",
                "target_id": "AGENT-001",
                "target_type": "agent",
                "operation": "update",
                "status": "pending"
            }
        }


class SyncConflict(BaseModel):
    """Sync conflict model"""
    id: str = Field(..., description="Unique conflict ID")
    item_id: str = Field(..., description="Item ID")
    local_version: Dict[str, Any] = Field(..., description="Local version")
    remote_version: Dict[str, Any] = Field(..., description="Remote version")
    conflict_type: str = Field(..., description="Conflict type")
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "CONFLICT-001",
                "item_id": "INV-001",
                "conflict_type": "concurrent_update"
            }
        }


class UpdateInventoryRequest(BaseModel):
    """Request model for updating inventory"""
    booked_seats: Optional[int] = None
    available_seats: Optional[int] = None
    held_seats: Optional[int] = None


class CreateSyncConfigRequest(BaseModel):
    """Request model for creating sync config"""
    enabled: bool
    sync_targets: List[SyncTarget]
    sync_frequency: str = "realtime"
    offline_mode: bool = True


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
