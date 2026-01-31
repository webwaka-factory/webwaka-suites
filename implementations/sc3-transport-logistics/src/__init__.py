"""
SC-3 Transport & Logistics Suite V1

A comprehensive suite for inter-city transport and logistics operations with
ticketing, seat allocation, ticket verification, and marketplace models
supporting both SVM (transport companies) and MVM (motor parks) with
realtime-enhanced but offline-safe inventory synchronization.
"""

__version__ = "1.0.0"
__author__ = "Manus AI"
__description__ = "Transport & Logistics Suite V1 for WebWaka Platform"

# Import core models
from src.models import (
    Booking,
    Ticket,
    Payment,
    Seat,
    SeatMap,
    TicketVerification,
    BoardingPass,
    TransportOperator,
    Route,
    Schedule,
    Vehicle,
    InventoryItem,
    InventorySyncConfig,
)

__all__ = [
    "Booking",
    "Ticket",
    "Payment",
    "Seat",
    "SeatMap",
    "TicketVerification",
    "BoardingPass",
    "TransportOperator",
    "Route",
    "Schedule",
    "Vehicle",
    "InventoryItem",
    "InventorySyncConfig",
]
