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
            def expected_uuid(self) -> str:
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
        assert len(service.name) > 0

    def test_service_process_characteristics_method(self, service: BaseGattService) -> None:
        """Test that service has process_characteristics method."""
        assert hasattr(service, "process_characteristics")
        assert callable(service.process_characteristics)

    def test_service_creation(self, service: BaseGattService) -> None:
        """Test service instantiation."""
        assert service is not None

    def test_expected_characteristics_defined(self, service: BaseGattService) -> None:
        """Test that service defines expected characteristics."""
        expected = service.get_expected_characteristics()
        assert isinstance(expected, dict)
        assert len(expected) > 0  # Services should have at least one characteristic

    def test_required_subset_of_expected(self, service: BaseGattService) -> None:
        """Test that required characteristics are a subset of expected ones."""
        expected = service.get_expected_characteristics()
        required = service.get_required_characteristics()
        required_keys = set(required.keys())
        expected_keys = set(expected.keys())
        assert required_keys.issubset(expected_keys), "Required characteristics must be subset of expected"


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
