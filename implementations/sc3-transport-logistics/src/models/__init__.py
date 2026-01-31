"""
SC-3 Transport & Logistics Suite V1 - Data Models

This module contains all data models for the transport and logistics suite including:
- Ticketing (bookings, tickets, payments)
- Seat allocation (seats, seat maps, holds)
- Verification (ticket verification, boarding passes)
- Marketplace (operators, routes, schedules, vehicles)
- Inventory (items, sync config, offline queue)
"""

from src.models.ticketing import (
    Booking,
    Ticket,
    Payment,
    BookingStatus,
    PaymentStatus,
    TicketStatus,
)
from src.models.seat_allocation import (
    Seat,
    SeatMap,
    SeatHold,
    SeatStatus,
    SeatType,
)
from src.models.verification import (
    TicketVerification,
    BoardingPass,
    VerificationLog,
    VerificationStatus,
    BoardingPassStatus,
)
from src.models.marketplace import (
    TransportOperator,
    Route,
    Schedule,
    Vehicle,
    OperatorStatus,
    RouteStatus,
)
from src.models.inventory import (
    InventoryItem,
    InventorySyncConfig,
    InventorySyncEvent,
    OfflineSyncQueue,
    SyncConflict,
    SyncStatus,
    SyncTarget,
)

__all__ = [
    # Ticketing
    "Booking",
    "Ticket",
    "Payment",
    "BookingStatus",
    "PaymentStatus",
    "TicketStatus",
    # Seat Allocation
    "Seat",
    "SeatMap",
    "SeatHold",
    "SeatStatus",
    "SeatType",
    # Verification
    "TicketVerification",
    "BoardingPass",
    "VerificationLog",
    "VerificationStatus",
    "BoardingPassStatus",
    # Marketplace
    "TransportOperator",
    "Route",
    "Schedule",
    "Vehicle",
    "OperatorStatus",
    "RouteStatus",
    # Inventory
    "InventoryItem",
    "InventorySyncConfig",
    "InventorySyncEvent",
    "OfflineSyncQueue",
    "SyncConflict",
    "SyncStatus",
    "SyncTarget",
]
