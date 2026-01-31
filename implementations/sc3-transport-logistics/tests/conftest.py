"""
SC-3 Transport & Logistics Suite - Test Configuration

Shared fixtures and configuration for all tests.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi.testclient import TestClient
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api.server import app
from src.models.ticketing import (
    Booking, BookingStatus, PaymentStatus,
    Ticket, TicketStatus, Payment
)
from src.models.seat_allocation import (
    Seat, SeatStatus, SeatType, SeatMap, SeatHold
)
from src.models.verification import (
    TicketVerification, VerificationStatus,
    BoardingPass, BoardingPassStatus, VerificationLog
)


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_booking() -> Dict[str, Any]:
    """Create sample booking data"""
    return {
        "id": "BK-001",
        "customer_id": "CUST-001",
        "route_id": "RT-001",
        "journey_date": datetime.utcnow() + timedelta(days=1),
        "status": BookingStatus.PENDING,
        "seats": ["A1", "A2"],
        "total_price": 50.00,
        "payment_status": PaymentStatus.PENDING,
        "booking_reference": "BK20240130001",
        "customer_name": "John Doe",
        "customer_phone": "+2348012345678",
        "customer_email": "john.doe@example.com",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_ticket() -> Dict[str, Any]:
    """Create sample ticket data"""
    return {
        "id": "TK-001",
        "booking_id": "BK-001",
        "seat_id": "SEAT-001",
        "route_id": "RT-001",
        "journey_date": datetime.utcnow() + timedelta(days=1),
        "status": TicketStatus.ISSUED,
        "ticket_number": "TK20240130001",
        "qr_code": "QR_DATA_TK001",
        "passenger_name": "John Doe",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_payment() -> Dict[str, Any]:
    """Create sample payment data"""
    return {
        "id": "PAY-001",
        "booking_id": "BK-001",
        "amount": 50.00,
        "currency": "NGN",
        "status": PaymentStatus.PENDING,
        "payment_method": "card",
        "payment_gateway": "paystack",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_seat() -> Dict[str, Any]:
    """Create sample seat data"""
    return {
        "id": "SEAT-001",
        "vehicle_id": "VEH-001",
        "seat_number": "A1",
        "row": 1,
        "column": 1,
        "seat_type": SeatType.STANDARD,
        "status": SeatStatus.AVAILABLE,
        "price": 25.00,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_seat_map() -> Dict[str, Any]:
    """Create sample seat map data"""
    seats = []
    for row in range(1, 11):
        for col in range(1, 5):
            seat_num = f"{chr(64 + row)}{col}"
            seats.append({
                "id": f"SEAT-{row:02d}{col}",
                "vehicle_id": "VEH-001",
                "seat_number": seat_num,
                "row": row,
                "column": col,
                "seat_type": SeatType.STANDARD,
                "status": SeatStatus.AVAILABLE,
                "price": 25.00,
            })
    
    return {
        "id": "MAP-001",
        "vehicle_id": "VEH-001",
        "total_seats": 40,
        "rows": 10,
        "columns": 4,
        "seats": seats,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_boarding_pass() -> Dict[str, Any]:
    """Create sample boarding pass data"""
    return {
        "id": "BP-001",
        "ticket_id": "TK-001",
        "booking_id": "BK-001",
        "status": BoardingPassStatus.ISSUED,
        "boarding_number": "BP001",
        "boarding_time": datetime.utcnow() + timedelta(hours=1),
        "gate": "Gate A",
        "seat_number": "A1",
        "passenger_name": "John Doe",
        "route_from": "Lagos",
        "route_to": "Abuja",
        "journey_date": datetime.utcnow() + timedelta(days=1),
        "vehicle_number": "VEH-001",
        "qr_code": "QR_DATA_BP001",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_verification() -> Dict[str, Any]:
    """Create sample verification data"""
    return {
        "id": "VER-001",
        "ticket_id": "TK-001",
        "qr_code": "QR_DATA_TK001",
        "status": VerificationStatus.VALID,
        "created_at": datetime.utcnow(),
    }


@pytest.fixture
def nigeria_routes() -> List[Dict[str, Any]]:
    """Create sample Nigeria routes (INV-007)"""
    return [
        {
            "id": "RT-LAG-ABJ",
            "name": "Lagos to Abuja",
            "from_city": "Lagos",
            "to_city": "Abuja",
            "distance_km": 750,
            "duration_hours": 9,
            "base_price": 15000,  # NGN
        },
        {
            "id": "RT-LAG-PH",
            "name": "Lagos to Port Harcourt",
            "from_city": "Lagos",
            "to_city": "Port Harcourt",
            "distance_km": 580,
            "duration_hours": 7,
            "base_price": 12000,  # NGN
        },
        {
            "id": "RT-ABJ-KAN",
            "name": "Abuja to Kano",
            "from_city": "Abuja",
            "to_city": "Kano",
            "distance_km": 480,
            "duration_hours": 6,
            "base_price": 10000,  # NGN
        },
    ]


@pytest.fixture
def nigeria_operators() -> List[Dict[str, Any]]:
    """Create sample Nigeria transport operators (INV-007)"""
    return [
        {
            "id": "OP-001",
            "name": "ABC Transport",
            "license_number": "NG-TRN-001",
            "contact_phone": "+2348012345678",
            "fleet_size": 50,
            "routes": ["RT-LAG-ABJ", "RT-LAG-PH"],
        },
        {
            "id": "OP-002",
            "name": "God Is Good Motors",
            "license_number": "NG-TRN-002",
            "contact_phone": "+2348023456789",
            "fleet_size": 75,
            "routes": ["RT-LAG-ABJ", "RT-ABJ-KAN"],
        },
        {
            "id": "OP-003",
            "name": "Peace Mass Transit",
            "license_number": "NG-TRN-003",
            "contact_phone": "+2348034567890",
            "fleet_size": 100,
            "routes": ["RT-LAG-ABJ", "RT-LAG-PH", "RT-ABJ-KAN"],
        },
    ]
