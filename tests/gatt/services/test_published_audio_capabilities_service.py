"""Tests for PublishedAudioCapabilities Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.published_audio_capabilities import PublishedAudioCapabilitiesService
from bluetooth_sig.types.gatt_enums import CharacteristicName

from .test_service_common import CommonServiceTests


class TestPublishedAudioCapabilitiesService(CommonServiceTests):
    """PublishedAudioCapabilities Service tests."""

    @pytest.fixture
    def service(self) -> PublishedAudioCapabilitiesService:
        """Provide the service instance."""
        return PublishedAudioCapabilitiesService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for PublishedAudioCapabilities."""
        return "1850"

    def test_characteristics_defined(self, service: PublishedAudioCapabilitiesService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 6

    def test_required_characteristics(self, service: PublishedAudioCapabilitiesService) -> None:
        """Test that required characteristics are correctly marked."""
        required = service.get_required_characteristics()
        assert len(required) == 2
        assert CharacteristicName.AVAILABLE_AUDIO_CONTEXTS in required
        assert CharacteristicName.SUPPORTED_AUDIO_CONTEXTS in required
