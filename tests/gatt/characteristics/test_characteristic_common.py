"""Common test utilities and fixtures for characteristic tests."""

from __future__ import annotations

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


class CommonCharacteristicTests:
    """Base class for common characteristic test patterns.

    Inherit from this class in characteristic test files to get standard tests.

    Example:
        class TestBatteryLevelCharacteristic(CommonCharacteristicTests):
            @pytest.fixture
            def characteristic(self) -> BaseCharacteristic:
                return BatteryLevelCharacteristic()

            @pytest.fixture
            def expected_uuid(self) -> str:
                return "2A19"

            @pytest.fixture
            def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
                return bytearray([75])  # 75% battery
    """

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        """Default: fail with clear error if not overridden in subclass."""
        raise NotImplementedError(
            f"Test incomplete: missing 'characteristic' fixture in {type(self).__name__}. "
            "Override this fixture in your test class."
        )

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Default: fail with clear error if not overridden in subclass."""
        raise NotImplementedError(
            f"Test incomplete: missing 'expected_uuid' fixture in {type(self).__name__}. "
            "Override this fixture in your test class."
        )

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData:
        """Default: fail with clear error if not overridden in subclass."""
        raise NotImplementedError(
            f"Test incomplete: missing 'valid_test_data' fixture in {type(self).__name__}. "
            "Override this fixture in your test class."
        )

    # === Behavioral Tests ===
    def test_characteristic_uuid_matches_expected(self, characteristic: BaseCharacteristic, expected_uuid: str) -> None:
        """Test that characteristic UUID matches the expected value."""
        assert characteristic.uuid == expected_uuid

    def test_parse_valid_data_succeeds(
        self, characteristic: BaseCharacteristic, valid_test_data: CharacteristicTestData | list[CharacteristicTestData]
    ) -> None:
        """Test parsing valid data succeeds and returns meaningful result."""
        # Handle both single and multiple test cases
        test_cases = valid_test_data if isinstance(valid_test_data, list) else [valid_test_data]

        for i, test_case in enumerate(test_cases):
            input_data = test_case.input_data

            result = characteristic.parse_value(input_data)

            # Should succeed without field errors
            case_desc = f"Test case {i + 1} ({test_case.description})"
            assert not result.field_errors, (
                f"{case_desc}: Valid data should parse without errors: {result.field_errors}"
            )
            assert result.parse_success, f"{case_desc}: parse_success should be True for valid data"
            assert result.value is not None, f"{case_desc}: Parsed value should not be None for valid data"
            assert result.info.uuid == characteristic.uuid, f"{case_desc}: Result info should match characteristic"

            # CRITICAL: Validate that the parsed value matches expected value
            self._assert_values_equal(
                result.value,
                test_case.expected_value,
                f"parse_value result (test case {i + 1}: {test_case.description})",
            )

    def test_decode_valid_data_returns_expected_value(
        self, characteristic: BaseCharacteristic, valid_test_data: CharacteristicTestData | list[CharacteristicTestData]
    ) -> None:
        """Test raw decoding returns the exact expected value."""
        # Handle both single and multiple test cases
        test_cases = valid_test_data if isinstance(valid_test_data, list) else [valid_test_data]

        for i, test_case in enumerate(test_cases):
            input_data = test_case.input_data

            result = characteristic.decode_value(input_data)
            case_desc = f"Test case {i + 1} ({test_case.description})"
            assert result is not None, f"{case_desc}: decode_value should return a value, not None"

            # CRITICAL: Validate that the decoded value exactly matches expected value
            self._assert_values_equal(
                result, test_case.expected_value, f"decode_value result (test case {i + 1}: {test_case.description})"
            )

    def _assert_values_equal(self, actual: object, expected: object, context: str) -> None:
        """Assert two values are equal with tolerance for floating point."""
        if isinstance(expected, float) and isinstance(actual, float):
            # Handle floating point precision
            tolerance = 1e-10
            assert abs(actual - expected) < tolerance, (
                f"{context}: expected {expected}, got {actual} (diff: {abs(actual - expected)})"
            )
        elif hasattr(expected, "__struct_fields__"):
            # Handle msgspec structs with potential float fields
            assert isinstance(actual, type(expected)), (
                f"{context}: type mismatch - expected {type(expected)}, got {type(actual)}"
            )
            for field_name in expected.__struct_fields__:  # type: ignore[attr-defined]
                expected_field = getattr(expected, field_name)
                actual_field = getattr(actual, field_name)
                self._assert_values_equal(actual_field, expected_field, f"{context}.{field_name}")
        else:
            # Direct equality for all other types
            assert actual == expected, f"{context}: expected {expected}, got {actual}"

    def test_empty_data_handling(self, characteristic: BaseCharacteristic) -> None:
        """Test that empty data is handled appropriately."""
        result = characteristic.parse_value(bytearray())

        # Should either succeed (for variable-length) or fail gracefully with meaningful error
        if not result.parse_success:
            # If it fails, should have a meaningful error message (not just empty)
            assert result.error_message.strip(), "Failed parsing should have meaningful error message"

    def test_oversized_data_validation(
        self, characteristic: BaseCharacteristic, valid_test_data: CharacteristicTestData | list[CharacteristicTestData]
    ) -> None:
        """Test that excessively large data is properly validated."""
        # Use first test case if list, otherwise use single test case
        test_case = valid_test_data[0] if isinstance(valid_test_data, list) else valid_test_data
        input_data = test_case.input_data

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

    def test_length_validation_behaviour(self, characteristic: BaseCharacteristic) -> None:
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

    def test_range_validation_behaviour(
        self, characteristic: BaseCharacteristic, valid_test_data: CharacteristicTestData | list[CharacteristicTestData]
    ) -> None:
        """Test that characteristics handle malformed data appropriately."""
        # Use first test case if list, otherwise use single test case
        test_case = valid_test_data[0] if isinstance(valid_test_data, list) else valid_test_data

        # Test with clearly invalid data patterns that should fail parsing
        invalid_patterns = [
            bytearray([0xFF, 0xFF, 0xFF, 0xFF]),  # All high bits
            bytearray([0x00, 0x00, 0x00, 0x00]),  # All zeros (might be valid for some)
        ]

        for invalid_data in invalid_patterns:
            # Only test if the invalid data is different length than valid data
            # to avoid testing valid data patterns
            if len(invalid_data) != len(test_case.input_data):
                result = characteristic.parse_value(invalid_data)
                # Should either fail parsing or handle gracefully
                if not result.parse_success:
                    assert result.error_message.strip(), "Failed parsing should have meaningful error message"
                # If it succeeds, that's also acceptable (some characteristics are very tolerant)

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

    def test_decode_exception_handling(self, characteristic: BaseCharacteristic) -> None:
        """Test that decode_value handles extreme cases gracefully."""
        extreme_cases = [
            bytearray([0xFF] * 1000),  # Massive data
            bytearray([0x00]),  # Single zero byte
            bytearray([0xFF]),  # Single max byte
        ]

        for test_data in extreme_cases:
            try:
                characteristic.decode_value(test_data)
                # If it succeeds, that's fine - no crash is good
            except Exception as e:
                # If it fails, should have meaningful error message
                assert str(e).strip(), f"Exception should have meaningful message: {e}"

    def test_undersized_data_handling(
        self, characteristic: BaseCharacteristic, valid_test_data: CharacteristicTestData | list[CharacteristicTestData]
    ) -> None:
        """Test handling of data that's too short."""
        # Use first test case if list, otherwise use single test case
        test_case = valid_test_data[0] if isinstance(valid_test_data, list) else valid_test_data

        if len(test_case.input_data) > 1:
            short_data = test_case.input_data[:-1]  # Remove last byte
            result = characteristic.parse_value(short_data)
            # Should either parse successfully or fail gracefully with error
            if not result.parse_success:
                assert result.error_message.strip(), "Should have meaningful error for short data"

    def test_parse_decode_consistency(
        self, characteristic: BaseCharacteristic, valid_test_data: CharacteristicTestData | list[CharacteristicTestData]
    ) -> None:
        """Test that parse_value and decode_value return consistent results."""
        # Use first test case if list, otherwise use single test case
        test_case = valid_test_data[0] if isinstance(valid_test_data, list) else valid_test_data
        input_data = test_case.input_data

        parse_result = characteristic.parse_value(input_data)
        decode_result = characteristic.decode_value(input_data)

        if parse_result.parse_success:
            # If parsing succeeded, the values should be equivalent
            self._assert_values_equal(parse_result.value, decode_result, "parse vs decode consistency")

    def test_round_trip(
        self, characteristic: BaseCharacteristic, valid_test_data: CharacteristicTestData | list[CharacteristicTestData]
    ) -> None:
        """Test that encoding and decoding preserve data (round trip)."""
        test_cases = valid_test_data if isinstance(valid_test_data, list) else [valid_test_data]

        for i, test_case in enumerate(test_cases):
            case_desc = f"Test case {i + 1} ({test_case.description})"
            parsed = characteristic.decode_value(test_case.input_data)
            encoded = characteristic.encode_value(parsed)
            assert encoded == test_case.input_data, f"{case_desc}: Round trip failed - encoded data differs from input"


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
