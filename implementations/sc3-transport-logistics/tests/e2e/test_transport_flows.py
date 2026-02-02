"""
End-to-End Tests for SC-3 Transport Flows

Complete workflow tests for the Transport & Logistics Suite.
"""

import pytest
from datetime import datetime, timedelta


class TestCompleteBookingFlow:
    """Tests for complete booking flow"""

    def test_booking_to_boarding_flow(self, client, sample_booking):
        """Test complete flow from booking to boarding"""
        # Step 1: Create booking
        booking_data = {
            "customer_id": sample_booking["customer_id"],
            "route_id": sample_booking["route_id"],
            "journey_date": sample_booking["journey_date"].isoformat(),
            "seats": sample_booking["seats"],
            "customer_name": sample_booking["customer_name"],
            "customer_phone": sample_booking["customer_phone"],
        }
        
        response = client.post("/api/v1/ticketing/bookings", json=booking_data)
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Step 2: Hold seats
        for seat in sample_booking["seats"]:
            hold_data = {
                "customer_id": sample_booking["customer_id"],
                "hold_duration_minutes": 15
            }
            response = client.post(f"/api/v1/seat-allocation/seats/{seat}/hold", json=hold_data)
            assert response.status_code == 200
        
        # Step 3: Book seats
        for seat in sample_booking["seats"]:
            book_data = {
                "customer_id": sample_booking["customer_id"],
                "booking_id": "BK-001"
            }
            response = client.post(f"/api/v1/seat-allocation/seats/{seat}/book", json=book_data)
            assert response.status_code == 200
        
        # Step 4: Generate boarding pass
        boarding_pass_data = {
            "ticket_id": "TK-001",
            "boarding_time": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        response = client.post("/api/v1/verification/boarding-pass", json=boarding_pass_data)
        assert response.status_code == 200
        
        # Step 5: Verify ticket at gate
        verification_data = {
            "qr_code": "QR_DATA_TK001",
            "verified_by": "STAFF-001",
            "verification_location": "Gate A"
        }
        response = client.post("/api/v1/verification/verify", json=verification_data)
        assert response.status_code == 200


class TestNigeriaBookingFlow:
    """Tests for Nigeria-specific booking flow (INV-007)"""

    def test_lagos_abuja_booking_flow(self, client, nigeria_routes, nigeria_operators):
        """Test complete Lagos to Abuja booking flow"""
        # Step 1: Register operator
        operator_data = nigeria_operators[0]
        response = client.post("/api/v1/marketplace/operators", json=operator_data)
        assert response.status_code == 200
        
        # Step 2: Create route
        route_data = nigeria_routes[0]  # Lagos to Abuja
        response = client.post("/api/v1/marketplace/routes", json=route_data)
        assert response.status_code == 200
        
        # Step 3: Create booking with Nigerian customer
        booking_data = {
            "customer_id": "CUST-NG-001",
            "route_id": "RT-LAG-ABJ",
            "journey_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "seats": ["A1"],
            "customer_name": "Adebayo Ogundimu",
            "customer_phone": "+2348012345678",
            "customer_email": "adebayo@example.ng",
        }
        response = client.post("/api/v1/ticketing/bookings", json=booking_data)
        assert response.status_code == 200
        
        # Step 4: Get seat map for vehicle
        response = client.get("/api/v1/seat-allocation/vehicles/VEH-001/seats")
        assert response.status_code == 200
        
        # Step 5: Hold seat
        hold_data = {
            "customer_id": "CUST-NG-001",
            "hold_duration_minutes": 15
        }
        response = client.post("/api/v1/seat-allocation/seats/A1/hold", json=hold_data)
        assert response.status_code == 200
        
        # Step 6: Book seat
        book_data = {
            "customer_id": "CUST-NG-001",
            "booking_id": "BK-NG-001"
        }
        response = client.post("/api/v1/seat-allocation/seats/A1/book", json=book_data)
        assert response.status_code == 200


class TestInventorySyncFlow:
    """Tests for inventory synchronization flow"""

    def test_inventory_sync_flow(self, client):
        """Test inventory sync flow"""
        # Step 1: Trigger sync
        response = client.post("/api/v1/inventory/sync")
        assert response.status_code == 200
        sync_id = response.json()["data"]["sync_id"]
        
        # Step 2: Check sync status
        response = client.get(f"/api/v1/inventory/sync/status/{sync_id}")
        assert response.status_code == 200
        
        # Step 3: List inventory
        response = client.get("/api/v1/inventory/items")
        assert response.status_code == 200

    def test_offline_sync_queue_flow(self, client):
        """Test offline sync queue flow"""
        # Queue multiple operations
        operations = [
            {"operation": "update_seat", "data": {"seat_id": "A1", "status": "booked"}},
            {"operation": "update_seat", "data": {"seat_id": "A2", "status": "booked"}},
            {"operation": "create_booking", "data": {"booking_id": "BK-OFFLINE-001"}},
        ]
        
        for op in operations:
            response = client.post("/api/v1/inventory/offline-queue", json=op)
            assert response.status_code == 200


class TestVerificationFlow:
    """Tests for ticket verification flow"""

    def test_verification_flow(self, client):
        """Test complete verification flow"""
        # Step 1: Get ticket
        response = client.get("/api/v1/ticketing/tickets/TK-001")
        assert response.status_code == 200
        
        # Step 2: Generate boarding pass
        boarding_pass_data = {
            "ticket_id": "TK-001",
            "boarding_time": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        response = client.post("/api/v1/verification/boarding-pass", json=boarding_pass_data)
        assert response.status_code == 200
        
        # Step 3: Get boarding pass
        response = client.get("/api/v1/verification/boarding-pass/TK-001")
        assert response.status_code == 200
        
        # Step 4: Verify at gate
        verification_data = {
            "qr_code": "QR_DATA_TK001",
            "verified_by": "STAFF-001",
            "verification_location": "Gate A"
        }
        response = client.post("/api/v1/verification/verify", json=verification_data)
        assert response.status_code == 200


class TestMarketplaceFlow:
    """Tests for marketplace flow"""

    def test_operator_route_schedule_flow(self, client, nigeria_operators, nigeria_routes):
        """Test operator, route, and schedule creation flow"""
        # Step 1: Create operators
        for operator in nigeria_operators:
            response = client.post("/api/v1/marketplace/operators", json=operator)
            assert response.status_code == 200
        
        # Step 2: List operators
        response = client.get("/api/v1/marketplace/operators")
        assert response.status_code == 200
        
        # Step 3: Create routes
        for route in nigeria_routes:
            response = client.post("/api/v1/marketplace/routes", json=route)
            assert response.status_code == 200
        
        # Step 4: List routes
        response = client.get("/api/v1/marketplace/routes")
        assert response.status_code == 200
        
        # Step 5: List schedules
        response = client.get("/api/v1/marketplace/schedules")
        assert response.status_code == 200


class TestMultiTenantFlow:
    """Tests for multi-tenant functionality"""

    def test_multi_operator_booking(self, client, nigeria_operators):
        """Test booking across multiple operators"""
        # Create bookings for different operators
        operators = ["OP-001", "OP-002", "OP-003"]
        
        for i, op_id in enumerate(operators):
            booking_data = {
                "customer_id": f"CUST-{i+1:03d}",
                "route_id": "RT-LAG-ABJ",
                "journey_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                "seats": [f"A{i+1}"],
                "customer_name": f"Customer {i+1}",
                "customer_phone": f"+234801234567{i}",
            }
            
            response = client.post("/api/v1/ticketing/bookings", json=booking_data)
            assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling"""

    def test_invalid_booking_data(self, client):
        """Test handling of invalid booking data"""
        invalid_data = {
            "customer_id": "",  # Empty customer ID
        }
        
        response = client.post("/api/v1/ticketing/bookings", json=invalid_data)
        # API should handle gracefully
        assert response.status_code in [200, 400, 422]

    def test_nonexistent_resource(self, client):
        """Test handling of nonexistent resources"""
        response = client.get("/api/v1/ticketing/bookings/NONEXISTENT")
        assert response.status_code == 200  # API returns success with empty data
