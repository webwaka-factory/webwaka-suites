"""
Unit Tests for SC-3 Seat Allocation Models

Tests for Seat, SeatMap, and SeatHold models.
"""

import pytest
from datetime import datetime, timedelta

from src.models.seat_allocation import (
    Seat, SeatStatus, SeatType, SeatMap, SeatHold,
    UpdateSeatRequest, HoldSeatRequest, BookSeatRequest,
    SeatResponse, SeatMapResponse
)


class TestSeatModel:
    """Tests for Seat model"""

    def test_create_seat(self, sample_seat):
        """Test creating a seat"""
        seat = Seat(**sample_seat)
        
        assert seat.id == "SEAT-001"
        assert seat.vehicle_id == "VEH-001"
        assert seat.seat_number == "A1"
        assert seat.status == SeatStatus.AVAILABLE

    def test_seat_types(self, sample_seat):
        """Test different seat types"""
        # Standard seat
        seat = Seat(**sample_seat)
        assert seat.seat_type == SeatType.STANDARD
        
        # Premium seat
        sample_seat["seat_type"] = SeatType.PREMIUM
        sample_seat["price"] = 35.00
        premium_seat = Seat(**sample_seat)
        assert premium_seat.seat_type == SeatType.PREMIUM
        assert premium_seat.price == 35.00
        
        # Accessibility seat
        sample_seat["seat_type"] = SeatType.ACCESSIBILITY
        access_seat = Seat(**sample_seat)
        assert access_seat.seat_type == SeatType.ACCESSIBILITY

    def test_seat_status_transitions(self, sample_seat):
        """Test seat status transitions"""
        seat = Seat(**sample_seat)
        
        # Available -> Held
        seat.status = SeatStatus.HELD
        seat.held_by = "CUST-001"
        seat.held_until = datetime.utcnow() + timedelta(minutes=15)
        assert seat.status == SeatStatus.HELD
        
        # Held -> Booked
        seat.status = SeatStatus.BOOKED
        seat.booked_by = "CUST-001"
        assert seat.status == SeatStatus.BOOKED

    def test_seat_blocking(self, sample_seat):
        """Test seat blocking"""
        seat = Seat(**sample_seat)
        seat.status = SeatStatus.BLOCKED
        
        assert seat.status == SeatStatus.BLOCKED

    def test_seat_position(self, sample_seat):
        """Test seat position"""
        seat = Seat(**sample_seat)
        
        assert seat.row == 1
        assert seat.column == 1

    def test_seat_pricing(self, sample_seat):
        """Test seat pricing"""
        seat = Seat(**sample_seat)
        assert seat.price == 25.00
        
        # Update price
        seat.price = 30.00
        assert seat.price == 30.00


class TestSeatMapModel:
    """Tests for SeatMap model"""

    def test_create_seat_map(self, sample_seat_map):
        """Test creating a seat map"""
        seat_map = SeatMap(**sample_seat_map)
        
        assert seat_map.id == "MAP-001"
        assert seat_map.vehicle_id == "VEH-001"
        assert seat_map.total_seats == 40
        assert seat_map.rows == 10
        assert seat_map.columns == 4
        assert len(seat_map.seats) == 40

    def test_seat_map_layout(self, sample_seat_map):
        """Test seat map layout"""
        seat_map = SeatMap(**sample_seat_map)
        
        # Check first seat
        first_seat = seat_map.seats[0]
        assert first_seat.row == 1
        assert first_seat.column == 1
        
        # Check last seat
        last_seat = seat_map.seats[-1]
        assert last_seat.row == 10
        assert last_seat.column == 4

    def test_seat_map_availability(self, sample_seat_map):
        """Test seat map availability"""
        seat_map = SeatMap(**sample_seat_map)
        
        available_seats = [s for s in seat_map.seats if s.status == SeatStatus.AVAILABLE]
        assert len(available_seats) == 40

    def test_nigerian_bus_layout(self):
        """Test Nigerian bus layout (INV-007)"""
        # Typical Nigerian inter-city bus has 50-60 seats
        seats = []
        for row in range(1, 13):
            for col in range(1, 5):
                seat_num = f"{chr(64 + row)}{col}"
                seats.append({
                    "id": f"SEAT-{row:02d}{col}",
                    "vehicle_id": "VEH-NG-001",
                    "seat_number": seat_num,
                    "row": row,
                    "column": col,
                    "seat_type": SeatType.STANDARD,
                    "status": SeatStatus.AVAILABLE,
                    "price": 15000.00,  # NGN
                })
        
        seat_map = SeatMap(
            id="MAP-NG-001",
            vehicle_id="VEH-NG-001",
            total_seats=48,
            rows=12,
            columns=4,
            seats=seats,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        assert seat_map.total_seats == 48
        assert len(seat_map.seats) == 48


class TestSeatHoldModel:
    """Tests for SeatHold model"""

    def test_create_seat_hold(self):
        """Test creating a seat hold"""
        hold = SeatHold(
            id="HOLD-001",
            seat_id="SEAT-001",
            held_by="CUST-001",
            held_at=datetime.utcnow(),
            hold_expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        
        assert hold.id == "HOLD-001"
        assert hold.seat_id == "SEAT-001"
        assert hold.held_by == "CUST-001"

    def test_seat_hold_expiration(self):
        """Test seat hold expiration"""
        hold = SeatHold(
            id="HOLD-001",
            seat_id="SEAT-001",
            held_by="CUST-001",
            held_at=datetime.utcnow(),
            hold_expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        
        # Check if hold is still valid
        assert hold.hold_expires_at > datetime.utcnow()

    def test_seat_hold_with_booking(self):
        """Test seat hold with booking"""
        hold = SeatHold(
            id="HOLD-001",
            seat_id="SEAT-001",
            held_by="CUST-001",
            held_at=datetime.utcnow(),
            hold_expires_at=datetime.utcnow() + timedelta(minutes=15),
            booking_id="BK-001"
        )
        
        assert hold.booking_id == "BK-001"


class TestUpdateSeatRequest:
    """Tests for UpdateSeatRequest model"""

    def test_update_seat_status(self):
        """Test updating seat status"""
        request = UpdateSeatRequest(status=SeatStatus.BLOCKED)
        assert request.status == SeatStatus.BLOCKED

    def test_update_seat_price(self):
        """Test updating seat price"""
        request = UpdateSeatRequest(price=30.00)
        assert request.price == 30.00


class TestHoldSeatRequest:
    """Tests for HoldSeatRequest model"""

    def test_hold_seat_request(self):
        """Test hold seat request"""
        request = HoldSeatRequest(
            customer_id="CUST-001",
            hold_duration_minutes=15
        )
        
        assert request.customer_id == "CUST-001"
        assert request.hold_duration_minutes == 15

    def test_hold_seat_default_duration(self):
        """Test default hold duration"""
        request = HoldSeatRequest(customer_id="CUST-001")
        assert request.hold_duration_minutes == 15


class TestBookSeatRequest:
    """Tests for BookSeatRequest model"""

    def test_book_seat_request(self):
        """Test book seat request"""
        request = BookSeatRequest(
            customer_id="CUST-001",
            booking_id="BK-001"
        )
        
        assert request.customer_id == "CUST-001"
        assert request.booking_id == "BK-001"


class TestResponseModels:
    """Tests for response models"""

    def test_seat_response_success(self, sample_seat):
        """Test successful seat response"""
        seat = Seat(**sample_seat)
        response = SeatResponse(
            success=True,
            message="Seat retrieved successfully",
            data=seat
        )
        
        assert response.success is True
        assert response.data.id == "SEAT-001"

    def test_seat_response_failure(self):
        """Test failed seat response"""
        response = SeatResponse(
            success=False,
            message="Seat not found",
            data=None
        )
        
        assert response.success is False
        assert response.data is None

    def test_seat_map_response(self, sample_seat_map):
        """Test seat map response"""
        seat_map = SeatMap(**sample_seat_map)
        response = SeatMapResponse(
            success=True,
            message="Seat map retrieved successfully",
            data=seat_map
        )
        
        assert response.success is True
        assert response.data.total_seats == 40
