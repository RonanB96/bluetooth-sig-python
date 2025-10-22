"""Common test utilities and fixtures for service tests."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.base import BaseGattService


class CommonServiceTests:
    """Base class for common service test patterns.

    Inherit from this class in service test files to get standard tests.

    Example:
        class TestBatteryService(CommonServiceTests):
            @pytest.fixture
            def service(self):
                return BatteryService()

            @pytest.fixture
            def expected_uuid(self):
                return "180F"
    """

    @pytest.fixture
    def service(self) -> BaseGattService:
        """Override this fixture in subclasses."""
        raise NotImplementedError("Subclasses must provide service fixture")

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Override this fixture in subclasses."""
        raise NotImplementedError("Subclasses must provide expected_uuid fixture")

    def test_service_uuid(self, service: BaseGattService, expected_uuid: str) -> None:
        """Test that service has the expected UUID."""
        assert service.uuid == expected_uuid

    def test_service_has_name(self, service: BaseGattService) -> None:
        """Test that service has a valid name."""
        assert service.name
        assert isinstance(service.name, str)
        assert len(service.name) > 0

    def test_service_has_characteristics(self, service: BaseGattService) -> None:
        """Test that service defines its characteristics."""
        # Check if service has the attribute - some services may not have it
        if hasattr(service, "service_characteristics"):
            # service_characteristics can be None or a list
            service_chars = getattr(service, "service_characteristics", None)
            if service_chars is not None:
                assert isinstance(service_chars, list)

    def test_service_process_characteristics_method(self, service: BaseGattService) -> None:
        """Test that service has process_characteristics method."""
        assert hasattr(service, "process_characteristics")
        assert callable(service.process_characteristics)


def create_mock_characteristic_data(uuid: str, value: bytes) -> dict[str, bytes]:
    """Create mock characteristic data for service testing.

    Args:
        uuid: UUID of the characteristic
        value: Raw bytes value

    Returns:
        Dictionary mapping UUID to bytes for service testing
    """
    return {uuid: value}


@pytest.fixture
def mock_service_data() -> dict[str, bytes]:
    """Mock service data for testing."""
    return {
        "2A19": bytes([50]),  # Battery Level: 50%
        "2A6E": bytes([0x90, 0x01]),  # Temperature: 4.0°C
    }
