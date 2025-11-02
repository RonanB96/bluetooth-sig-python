"""Tests for Generic Attribute Service."""

import pytest

from bluetooth_sig.gatt.services.generic_attribute import GenericAttributeService

from .test_service_common import CommonServiceTests


class TestGenericAttributeService(CommonServiceTests):
    """Test Generic Attribute Service implementation."""

    @pytest.fixture
    def service(self) -> GenericAttributeService:
        """Provide the service instance."""
        return GenericAttributeService()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Generic Attribute Service."""
        return "1801"
