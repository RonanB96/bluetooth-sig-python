"""Tests for VolumeControl Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.volume_control import VolumeControlService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestVolumeControlService(CommonServiceTests):
    """VolumeControl Service tests."""

    @pytest.fixture
    def service(self) -> VolumeControlService:
        """Provide the service instance."""
        return VolumeControlService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for VolumeControl."""
        return "1844"

    def test_characteristics_defined(self, service: VolumeControlService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 3

    def test_required_characteristics(self, service: VolumeControlService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 1
        assert CharacteristicName.VOLUME_STATE in required
