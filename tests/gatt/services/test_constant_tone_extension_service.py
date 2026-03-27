"""Tests for ConstantToneExtension Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.constant_tone_extension import ConstantToneExtensionService

from .test_service_common import CommonServiceTests


class TestConstantToneExtensionService(CommonServiceTests):
    """ConstantToneExtension Service tests."""

    @pytest.fixture
    def service(self) -> ConstantToneExtensionService:
        """Provide the service instance."""
        return ConstantToneExtensionService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for ConstantToneExtension."""
        return "184A"

    def test_characteristics_defined(self, service: ConstantToneExtensionService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert len(expected) == 6
