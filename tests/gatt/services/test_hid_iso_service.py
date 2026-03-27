"""Tests for HidIso Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.hid_iso import HidIsoService

from .test_service_common import CommonServiceTests


class TestHidIsoService(CommonServiceTests):
    """HidIso Service tests."""

    @pytest.fixture
    def service(self) -> HidIsoService:
        """Provide the service instance."""
        return HidIsoService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for HidIso."""
        return "185C"

    def test_characteristics_defined(self, service: HidIsoService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 2
