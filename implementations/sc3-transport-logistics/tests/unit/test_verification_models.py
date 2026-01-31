"""
Unit Tests for SC-3 Verification Models

Tests for TicketVerification, BoardingPass, and VerificationLog models.
"""

import pytest
from datetime import datetime, timedelta

from src.models.verification import (
    TicketVerification, VerificationStatus,
    BoardingPass, BoardingPassStatus, VerificationLog,
    VerifyTicketRequest, GenerateBoardingPassRequest,
    VerificationResponse, BoardingPassResponse
)


class TestTicketVerificationModel:
    """Tests for TicketVerification model"""

    def test_create_verification(self, sample_verification):
        """Test creating a verification"""
        verification = TicketVerification(**sample_verification)
        
        assert verification.id == "VER-001"
        assert verification.ticket_id == "TK-001"
        assert verification.status == VerificationStatus.VALID

    def test_verification_statuses(self, sample_verification):
        """Test different verification statuses"""
        # Valid
        verification = TicketVerification(**sample_verification)
        assert verification.status == VerificationStatus.VALID
        
        # Invalid
        sample_verification["status"] = VerificationStatus.INVALID
        invalid = TicketVerification(**sample_verification)
        assert invalid.status == VerificationStatus.INVALID
        
        # Expired
        sample_verification["status"] = VerificationStatus.EXPIRED
        expired = TicketVerification(**sample_verification)
        assert expired.status == VerificationStatus.EXPIRED
        
        # Already used
        sample_verification["status"] = VerificationStatus.ALREADY_USED
        used = TicketVerification(**sample_verification)
        assert used.status == VerificationStatus.ALREADY_USED
        
        # Not found
        sample_verification["status"] = VerificationStatus.NOT_FOUND
        not_found = TicketVerification(**sample_verification)
        assert not_found.status == VerificationStatus.NOT_FOUND

    def test_verification_with_details(self, sample_verification):
        """Test verification with details"""
        sample_verification["verified_at"] = datetime.utcnow()
        sample_verification["verified_by"] = "STAFF-001"
        sample_verification["verification_location"] = "Gate A"
        
        verification = TicketVerification(**sample_verification)
        
        assert verification.verified_at is not None
        assert verification.verified_by == "STAFF-001"
        assert verification.verification_location == "Gate A"


class TestBoardingPassModel:
    """Tests for BoardingPass model"""

    def test_create_boarding_pass(self, sample_boarding_pass):
        """Test creating a boarding pass"""
        boarding_pass = BoardingPass(**sample_boarding_pass)
        
        assert boarding_pass.id == "BP-001"
        assert boarding_pass.ticket_id == "TK-001"
        assert boarding_pass.status == BoardingPassStatus.ISSUED

    def test_boarding_pass_status_transitions(self, sample_boarding_pass):
        """Test boarding pass status transitions"""
        boarding_pass = BoardingPass(**sample_boarding_pass)
        
        # Issued -> Used
        boarding_pass.status = BoardingPassStatus.USED
        assert boarding_pass.status == BoardingPassStatus.USED

    def test_boarding_pass_cancellation(self, sample_boarding_pass):
        """Test boarding pass cancellation"""
        boarding_pass = BoardingPass(**sample_boarding_pass)
        boarding_pass.status = BoardingPassStatus.CANCELLED
        
        assert boarding_pass.status == BoardingPassStatus.CANCELLED

    def test_boarding_pass_details(self, sample_boarding_pass):
        """Test boarding pass details"""
        boarding_pass = BoardingPass(**sample_boarding_pass)
        
        assert boarding_pass.boarding_number == "BP001"
        assert boarding_pass.gate == "Gate A"
        assert boarding_pass.seat_number == "A1"
        assert boarding_pass.passenger_name == "John Doe"

    def test_boarding_pass_route(self, sample_boarding_pass):
        """Test boarding pass route information"""
        boarding_pass = BoardingPass(**sample_boarding_pass)
        
        assert boarding_pass.route_from == "Lagos"
        assert boarding_pass.route_to == "Abuja"

    def test_boarding_pass_qr_code(self, sample_boarding_pass):
        """Test boarding pass QR code"""
        boarding_pass = BoardingPass(**sample_boarding_pass)
        
        assert boarding_pass.qr_code == "QR_DATA_BP001"

    def test_nigerian_boarding_pass(self, sample_boarding_pass):
        """Test Nigerian boarding pass (INV-007)"""
        sample_boarding_pass["passenger_name"] = "Adebayo Ogundimu"
        sample_boarding_pass["route_from"] = "Lagos"
        sample_boarding_pass["route_to"] = "Abuja"
        sample_boarding_pass["vehicle_number"] = "LAG-123-XY"
        
        boarding_pass = BoardingPass(**sample_boarding_pass)
        
        assert boarding_pass.passenger_name == "Adebayo Ogundimu"
        assert boarding_pass.route_from == "Lagos"
        assert boarding_pass.route_to == "Abuja"


class TestVerificationLogModel:
    """Tests for VerificationLog model"""

    def test_create_verification_log(self):
        """Test creating a verification log"""
        log = VerificationLog(
            id="LOG-001",
            ticket_id="TK-001",
            verification_status=VerificationStatus.VALID,
            verified_at=datetime.utcnow(),
            verified_by="STAFF-001",
            verification_location="Gate A"
        )
        
        assert log.id == "LOG-001"
        assert log.ticket_id == "TK-001"
        assert log.verification_status == VerificationStatus.VALID

    def test_verification_log_with_device(self):
        """Test verification log with device info"""
        log = VerificationLog(
            id="LOG-001",
            ticket_id="TK-001",
            verification_status=VerificationStatus.VALID,
            verified_at=datetime.utcnow(),
            verified_by="STAFF-001",
            verification_location="Gate A",
            device_id="DEVICE-001"
        )
        
        assert log.device_id == "DEVICE-001"

    def test_verification_log_with_notes(self):
        """Test verification log with notes"""
        log = VerificationLog(
            id="LOG-001",
            ticket_id="TK-001",
            verification_status=VerificationStatus.INVALID,
            verified_at=datetime.utcnow(),
            verified_by="STAFF-001",
            verification_location="Gate A",
            notes="Ticket appears to be tampered"
        )
        
        assert log.notes == "Ticket appears to be tampered"


class TestVerifyTicketRequest:
    """Tests for VerifyTicketRequest model"""

    def test_verify_ticket_request(self):
        """Test verify ticket request"""
        request = VerifyTicketRequest(
            qr_code="QR_DATA_TK001",
            verified_by="STAFF-001",
            verification_location="Gate A"
        )
        
        assert request.qr_code == "QR_DATA_TK001"
        assert request.verified_by == "STAFF-001"
        assert request.verification_location == "Gate A"


class TestGenerateBoardingPassRequest:
    """Tests for GenerateBoardingPassRequest model"""

    def test_generate_boarding_pass_request(self):
        """Test generate boarding pass request"""
        request = GenerateBoardingPassRequest(
            ticket_id="TK-001",
            boarding_time=datetime.utcnow() + timedelta(hours=1)
        )
        
        assert request.ticket_id == "TK-001"
        assert request.boarding_time is not None


class TestResponseModels:
    """Tests for response models"""

    def test_verification_response_valid(self, sample_verification):
        """Test valid verification response"""
        verification = TicketVerification(**sample_verification)
        response = VerificationResponse(
            success=True,
            message="Ticket verified successfully",
            data=verification
        )
        
        assert response.success is True
        assert response.data.status == VerificationStatus.VALID

    def test_verification_response_invalid(self, sample_verification):
        """Test invalid verification response"""
        sample_verification["status"] = VerificationStatus.INVALID
        verification = TicketVerification(**sample_verification)
        response = VerificationResponse(
            success=False,
            message="Ticket verification failed",
            data=verification
        )
        
        assert response.success is False
        assert response.data.status == VerificationStatus.INVALID

    def test_boarding_pass_response(self, sample_boarding_pass):
        """Test boarding pass response"""
        boarding_pass = BoardingPass(**sample_boarding_pass)
        response = BoardingPassResponse(
            success=True,
            message="Boarding pass generated successfully",
            data=boarding_pass
        )
        
        assert response.success is True
        assert response.data.boarding_number == "BP001"
