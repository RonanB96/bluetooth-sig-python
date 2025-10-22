"""Common test utilities and fixtures for characteristic tests."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.types.uuid import BluetoothUUID


@dataclass
class CharacteristicTestData:
    """Test data structure that clearly shows input and expected output."""

    input_data: bytearray
    expected_value: Any
    description: str = ""


class CommonCharacteristicTests(ABC):
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

            @pytest.fixture
            def valid_test_data(self):
                return bytearray([75])  # 75% battery
    """

    @pytest.fixture
    @abstractmethod
    def characteristic(self) -> BaseCharacteristic:
        """Override this fixture in subclasses."""
        raise NotImplementedError("Subclasses must provide characteristic fixture")

    @pytest.fixture
    @abstractmethod
    def expected_uuid(self) -> str:
        """Override this fixture in subclasses."""
        raise NotImplementedError("Subclasses must provide expected_uuid fixture")

    @pytest.fixture
    @abstractmethod
    def valid_test_data(self) -> CharacteristicTestData:
        """Override this fixture in subclasses with representative valid data.

        Must return CharacteristicTestData with input_data and expected_value.
        """
        raise NotImplementedError("Subclasses must provide valid_test_data fixture")

    # === Behavioral Tests ===
    def test_characteristic_uuid_matches_expected(self, characteristic: BaseCharacteristic, expected_uuid: str) -> None:
        """Test that characteristic UUID matches the expected value."""
        assert characteristic.uuid == expected_uuid

    def test_parse_valid_data_succeeds(
        self, characteristic: BaseCharacteristic, valid_test_data: CharacteristicTestData
    ) -> None:
        """Test parsing valid data succeeds and returns meaningful result."""
        input_data = valid_test_data.input_data

        result = characteristic.parse_value(input_data)

        # Should succeed without field errors
        assert not result.field_errors, f"Valid data should parse without errors: {result.field_errors}"
        assert result.parse_success, "parse_success should be True for valid data"
        assert result.value is not None, "Parsed value should not be None for valid data"
        assert result.info.uuid == characteristic.uuid, "Result info should match characteristic"

    def test_decode_valid_data_returns_value(
        self, characteristic: BaseCharacteristic, valid_test_data: CharacteristicTestData
    ) -> None:
        """Test raw decoding valid data returns a non-None value."""
        input_data = valid_test_data.input_data

        result = characteristic.decode_value(input_data)
        assert result is not None, "decode_value should return a value, not None"

    def test_empty_data_handling(self, characteristic: BaseCharacteristic) -> None:
        """Test that empty data is handled appropriately."""
        result = characteristic.parse_value(bytearray())

        # Should either succeed (for variable-length) or fail gracefully with meaningful error
        if not result.parse_success:
            # If it fails, should have a meaningful error message (not just empty)
            assert result.error_message.strip(), "Failed parsing should have meaningful error message"

    def test_oversized_data_validation(
        self, characteristic: BaseCharacteristic, valid_test_data: CharacteristicTestData
    ) -> None:
        """Test that excessively large data is properly validated."""
        input_data = valid_test_data.input_data

        # Create data that's much larger than reasonable
        oversized_data = input_data + bytearray([0xFF] * 100)
        result = characteristic.parse_value(oversized_data)

        # For fixed-length characteristics, this should create validation errors
        # For variable-length, it might succeed but shouldn't crash
        if hasattr(characteristic, "expected_length") and characteristic.expected_length is not None:
            expected_len = characteristic.expected_length
            if len(oversized_data) > expected_len:
                assert not result.parse_success or result.field_errors, (
                    f"Oversized data ({len(oversized_data)} > {expected_len}) should trigger validation"
                )

    def test_length_validation_behavior(
        self, characteristic: BaseCharacteristic, valid_test_data: CharacteristicTestData
    ) -> None:
        """Test that length validation actually validates when configured."""
        # Test that characteristics with expected_length reject wrong-sized data
        if hasattr(characteristic, "expected_length") and characteristic.expected_length is not None:
            expected_len = characteristic.expected_length
            # Try with data that's too short
            if expected_len > 1:
                short_data = bytearray([0xFF] * (expected_len - 1))
                result = characteristic.parse_value(short_data)
                assert not result.parse_success, f"Should reject data shorter than {expected_len} bytes"

            # Try with data that's too long
            long_data = bytearray([0xFF] * (expected_len + 1))
            result = characteristic.parse_value(long_data)
            assert not result.parse_success, f"Should reject data longer than {expected_len} bytes"

    def test_range_validation_behavior(
        self, characteristic: BaseCharacteristic, valid_test_data: CharacteristicTestData
    ) -> None:
        """Test that range validation actually validates when configured."""
        # Only test if min/max values are set AND we can manipulate the test data meaningfully
        if (
            hasattr(characteristic, "min_value")
            and characteristic.min_value is not None
            and hasattr(characteristic, "max_value")
            and characteristic.max_value is not None
        ):
            # This test requires characteristics that parse to numeric values
            # and have controllable input data - skip if not applicable
            try:
                # Parse the valid data to see what type it produces
                valid_result = characteristic.decode_value(valid_test_data.input_data)
                if not isinstance(valid_result, (int, float)):
                    pytest.skip("Range validation test only applies to numeric characteristics")

                # We'd need to know how to construct invalid data for this specific characteristic
                # This is too characteristic-specific for a common test
                pytest.skip("Range validation requires characteristic-specific test data construction")

            except Exception:
                pytest.skip("Cannot determine characteristic value type for range testing")

    def test_uuid_resolution_behaviour(self, characteristic: BaseCharacteristic, expected_uuid: str) -> None:
        """Test that UUID resolution works and matches expected value."""
        # This tests actual behaviour: does the UUID resolution system work?

        converted_uuid = BluetoothUUID(expected_uuid)
        assert characteristic.uuid == converted_uuid, (
            f"UUID resolution failed: got {characteristic.uuid}, expected {converted_uuid}"
        )

        # Test that info.uuid matches the characteristic.uuid (consistency)
        info_uuid = str(characteristic.info.uuid)
        assert info_uuid.upper() == str(converted_uuid).upper(), "info.uuid should match characteristic.uuid"


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
