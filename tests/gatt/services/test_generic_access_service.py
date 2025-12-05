"""Tests for Generic Access Service."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.generic_access import GenericAccessService

from .test_service_common import CommonServiceTests


class TestGenericAccessService(CommonServiceTests):
    """Test Generic Access Service implementation."""

    @pytest.fixture
    def service(self) -> GenericAccessService:
        """Provide the service instance."""
        return GenericAccessService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Generic Access Service."""
        return "1800"
