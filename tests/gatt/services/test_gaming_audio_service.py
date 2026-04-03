"""Tests for GamingAudio Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.gaming_audio import GamingAudioService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestGamingAudioService(CommonServiceTests):
    """GamingAudio Service tests."""

    @pytest.fixture
    def service(self) -> GamingAudioService:
        """Provide the service instance."""
        return GamingAudioService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for GamingAudio."""
        return "1858"

    def test_characteristics_defined(self, service: GamingAudioService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 5

    def test_required_characteristics(self, service: GamingAudioService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 1
        assert CharacteristicName.GMAP_ROLE in required
