"""
Integration Tests for SC-3 API Endpoints

Tests for all API endpoints in the Transport & Logistics Suite.
"""

import pytest
from datetime import datetime, timedelta


class TestHealthEndpoints:
    """Tests for health check endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "SC-3 Transport & Logistics Suite V1"

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


class TestTicketingEndpoints:
    """Tests for ticketing endpoints"""

    def test_list_bookings(self, client):
        """Test list bookings endpoint"""
        response = client.get("/api/v1/ticketing/bookings")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    def test_create_booking(self, client, sample_booking):
        """Test create booking endpoint"""
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
        data = response.json()
        assert data["success"] is True

    def test_get_booking(self, client):
        """Test get booking endpoint"""
        response = client.get("/api/v1/ticketing/bookings/BK-001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "BK-001"

    def test_list_tickets(self, client):
        """Test list tickets endpoint"""
        response = client.get("/api/v1/ticketing/tickets")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_ticket(self, client):
        """Test get ticket endpoint"""
        response = client.get("/api/v1/ticketing/tickets/TK-001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestSeatAllocationEndpoints:
    """Tests for seat allocation endpoints"""

    def test_get_seat_map(self, client):
        """Test get seat map endpoint"""
        response = client.get("/api/v1/seat-allocation/vehicles/VEH-001/seats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["vehicle_id"] == "VEH-001"

    def test_hold_seat(self, client):
        """Test hold seat endpoint"""
        hold_data = {
            "customer_id": "CUST-001",
            "hold_duration_minutes": 15
        }
        
        response = client.post("/api/v1/seat-allocation/seats/SEAT-001/hold", json=hold_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "held"

    def test_book_seat(self, client):
        """Test book seat endpoint"""
        booking_data = {
            "customer_id": "CUST-001",
            "booking_id": "BK-001"
        }
        
        response = client.post("/api/v1/seat-allocation/seats/SEAT-001/book", json=booking_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "booked"


class TestVerificationEndpoints:
    """Tests for verification endpoints"""

    def test_verify_ticket(self, client):
        """Test verify ticket endpoint"""
        verification_data = {
            "qr_code": "QR_DATA_TK001",
            "verified_by": "STAFF-001",
            "verification_location": "Gate A"
        }
        
        response = client.post("/api/v1/verification/verify", json=verification_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_boarding_pass(self, client):
        """Test get boarding pass endpoint"""
        response = client.get("/api/v1/verification/boarding-pass/TK-001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_generate_boarding_pass(self, client):
        """Test generate boarding pass endpoint"""
        boarding_pass_data = {
            "ticket_id": "TK-001",
            "boarding_time": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        response = client.post("/api/v1/verification/boarding-pass", json=boarding_pass_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestMarketplaceEndpoints:
    """Tests for marketplace endpoints"""

    def test_list_operators(self, client):
        """Test list operators endpoint"""
        response = client.get("/api/v1/marketplace/operators")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_create_operator(self, client, nigeria_operators):
        """Test create operator endpoint"""
        operator_data = nigeria_operators[0]
        
        response = client.post("/api/v1/marketplace/operators", json=operator_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_list_routes(self, client):
        """Test list routes endpoint"""
        response = client.get("/api/v1/marketplace/routes")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_create_route(self, client, nigeria_routes):
        """Test create route endpoint"""
        route_data = nigeria_routes[0]
        
        response = client.post("/api/v1/marketplace/routes", json=route_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_list_schedules(self, client):
        """Test list schedules endpoint"""
        response = client.get("/api/v1/marketplace/schedules")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestInventoryEndpoints:
    """Tests for inventory endpoints"""

    def test_list_inventory(self, client):
        """Test list inventory endpoint"""
        response = client.get("/api/v1/inventory/items")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_trigger_inventory_sync(self, client):
        """Test trigger inventory sync endpoint"""
        response = client.post("/api/v1/inventory/sync")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "pending"

    def test_get_sync_status(self, client):
        """Test get sync status endpoint"""
        response = client.get("/api/v1/inventory/sync/status/SYNC-001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["sync_id"] == "SYNC-001"

    def test_queue_offline_sync(self, client):
        """Test queue offline sync endpoint"""
        queue_data = {
            "operation": "update_seat_status",
            "data": {"seat_id": "SEAT-001", "status": "booked"}
        }
        
        response = client.post("/api/v1/inventory/offline-queue", json=queue_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestNigeriaSpecificEndpoints:
    """Tests for Nigeria-specific functionality (INV-007)"""

    def test_lagos_abuja_route(self, client, nigeria_routes):
        """Test Lagos to Abuja route creation"""
        route_data = nigeria_routes[0]  # Lagos to Abuja
        
        response = client.post("/api/v1/marketplace/routes", json=route_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_nigerian_operator_registration(self, client, nigeria_operators):
        """Test Nigerian operator registration"""
        operator_data = nigeria_operators[0]  # ABC Transport
        
        response = client.post("/api/v1/marketplace/operators", json=operator_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_booking_with_nigerian_phone(self, client, sample_booking):
        """Test booking with Nigerian phone number"""
        booking_data = {
            "customer_id": "CUST-NG-001",
            "route_id": "RT-LAG-ABJ",
            "journey_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "seats": ["A1", "A2"],
            "customer_name": "Adebayo Ogundimu",
            "customer_phone": "+2348012345678",
        }
        
        response = client.post("/api/v1/ticketing/bookings", json=booking_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
