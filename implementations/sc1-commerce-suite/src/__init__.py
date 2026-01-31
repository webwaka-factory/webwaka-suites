"""
SC-1 Commerce Suite V1

A unified, feature-rich commerce suite that integrates four existing capabilities
(CB-1, CB-2, CB-3, CB-4) into a cohesive, user-facing product.

This is the first and largest suite to be built on the WebWaka platform.
"""

__version__ = "1.0.0"
__author__ = "Manus AI"
__description__ = "Commerce Suite V1 for WebWaka Platform"

# Import core modules
from src.models import (
    Order,
    Transaction,
    Product,
    Vendor,
    InventoryItem,
    Shipment,
    Invoice,
    LoyaltyProgram,
    Coupon,
    Subscription,
    Refund,
)

__all__ = [
    "Order",
    "Transaction",
    "Product",
    "Vendor",
    "InventoryItem",
    "Shipment",
    "Invoice",
    "LoyaltyProgram",
    "Coupon",
    "Subscription",
    "Refund",
]
