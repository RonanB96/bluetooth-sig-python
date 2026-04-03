"""Tests for BroadcastAudioScan Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.broadcast_audio_scan import BroadcastAudioScanService

from .test_service_common import CommonServiceTests


class TestBroadcastAudioScanService(CommonServiceTests):
    """BroadcastAudioScan Service tests."""

    @pytest.fixture
    def service(self) -> BroadcastAudioScanService:
        """Provide the service instance."""
        return BroadcastAudioScanService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for BroadcastAudioScan."""
        return "184F"

    def test_characteristics_defined(self, service: BroadcastAudioScanService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 2
