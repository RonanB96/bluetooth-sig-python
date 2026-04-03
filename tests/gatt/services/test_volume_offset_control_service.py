"""Tests for VolumeOffsetControl Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.volume_offset_control import VolumeOffsetControlService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestVolumeOffsetControlService(CommonServiceTests):
    """VolumeOffsetControl Service tests."""

    @pytest.fixture
    def service(self) -> VolumeOffsetControlService:
        """Provide the service instance."""
        return VolumeOffsetControlService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for VolumeOffsetControl."""
        return "1845"

    def test_characteristics_defined(self, service: VolumeOffsetControlService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 4

    def test_required_characteristics(self, service: VolumeOffsetControlService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 4
        assert CharacteristicName.VOLUME_OFFSET_STATE in required
