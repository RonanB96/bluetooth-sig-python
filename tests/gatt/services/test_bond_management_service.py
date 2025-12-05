"""Tests for Bond Management Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.bond_management import BondManagementService

from .test_service_common import CommonServiceTests


class TestBondManagementService(CommonServiceTests):
    """Test Bond Management Service implementation."""

    @pytest.fixture
    def service(self) -> BondManagementService:
        """Provide the service instance."""
        return BondManagementService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Bond Management Service."""
        return "181E"
