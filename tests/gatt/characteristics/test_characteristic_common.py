"""Common test utilities and fixtures for characteristic tests."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.types.gatt_enums import ValueType


class CommonCharacteristicTests:
    """Base class for common characteristic test patterns.

    Inherit from this class in characteristic test files to get standard tests.

    Example:
        class TestBatteryLevelCharacteristic(CommonCharacteristicTests):
            @pytest.fixture
            def characteristic(self):
                return BatteryLevelCharacteristic()

            @pytest.fixture
            def expected_uuid(self):
                return "2A19"
    """

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        """Override this fixture in subclasses."""
        raise NotImplementedError("Subclasses must provide characteristic fixture")

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Override this fixture in subclasses."""
        raise NotImplementedError("Subclasses must provide expected_uuid fixture")

    def test_characteristic_uuid(self, characteristic: BaseCharacteristic, expected_uuid: str) -> None:
        """Test that characteristic has the expected UUID."""
        assert characteristic.uuid == expected_uuid

    def test_characteristic_has_name(self, characteristic: BaseCharacteristic) -> None:
        """Test that characteristic has a valid name."""
        assert characteristic.name
        assert isinstance(characteristic.name, str)
        assert len(characteristic.name) > 0

    def test_characteristic_has_unit(self, characteristic: BaseCharacteristic) -> None:
        """Test that characteristic has a unit (can be empty string)."""
        assert hasattr(characteristic, "unit")
        assert isinstance(characteristic.unit, str)

    def test_characteristic_has_value_type(self, characteristic: BaseCharacteristic) -> None:
        """Test that characteristic has a valid value type."""
        assert hasattr(characteristic, "value_type")
        assert isinstance(characteristic.value_type, ValueType)

    def test_characteristic_decode_value_method(self, characteristic: BaseCharacteristic) -> None:
        """Test that characteristic has decode_value method."""
        assert hasattr(characteristic, "decode_value")
        assert callable(characteristic.decode_value)

    def test_characteristic_encode_value_method(self, characteristic: BaseCharacteristic) -> None:
        """Test that characteristic has encode_value method."""
        assert hasattr(characteristic, "encode_value")
        assert callable(characteristic.encode_value)


def create_test_context(
    device_name: str = "Test Device",
) -> CharacteristicContext:
    """Create a test context for characteristic parsing.

    Args:
        device_name: Name of the device

    Returns:
        CharacteristicContext for testing
    """
    from bluetooth_sig.types.context import DeviceInfo

    return CharacteristicContext(
        device_info=DeviceInfo(name=device_name),
    )


@pytest.fixture
def test_context() -> CharacteristicContext:
    """Default test context fixture."""
    return create_test_context()


# Common test data patterns
COMMON_INVALID_DATA = [
    bytearray(),  # Empty data
    bytearray([0xFF] * 100),  # Too much data
]
