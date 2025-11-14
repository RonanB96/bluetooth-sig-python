"""Common test utilities and fixtures for characteristic tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.types import CharacteristicDataProtocol
from bluetooth_sig.types.uuid import BluetoothUUID


@dataclass
class CharacteristicTestData:
    """Test data structure that clearly shows input and expected output."""

    input_data: bytearray
    expected_value: Any
    description: str = ""


@dataclass
class DependencyTestData:
    """Test data for dependency validation tests.

    Attributes:
        with_dependency_data: Test data when dependency is present (dict of UUID -> bytes)
        without_dependency_data: Test data when dependency is absent
        expected_with: Expected result when dependency present
        expected_without: Expected result when dependency absent (may be None if should fail)
        description: Description of this dependency scenario
    """

    with_dependency_data: dict[str, bytearray]
    without_dependency_data: bytearray
    expected_with: Any
    expected_without: Any | None
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
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Default: fail with clear error if not overridden in subclass."""
        raise NotImplementedError(
            f"Test incomplete: missing 'valid_test_data' fixture in {type(self).__name__}. "
            "Override this fixture in your test class."
        )

    @pytest.fixture
    def dependency_test_data(self) -> list[DependencyTestData] | None:
        """Optional: Provide dependency test data if characteristic has dependencies.

        Return None (default) if characteristic has no dependencies.
        Return list of DependencyTestData if characteristic has required/optional dependencies.

        This will be checked automatically - if dependencies exist but no test data provided,
        the test will fail with a clear error message.
        """
        return None

    # === Behavioral Tests ===
    def test_characteristic_uuid_matches_expected(self, characteristic: BaseCharacteristic, expected_uuid: str) -> None:
        """Test that characteristic UUID matches the expected value."""
        assert characteristic.uuid == expected_uuid

    def test_parse_valid_data_succeeds(
        self, characteristic: BaseCharacteristic, valid_test_data: list[CharacteristicTestData]
    ) -> None:
        """Test parsing valid data succeeds and returns meaningful result."""
        # Handle both single and multiple test cases
        if len(valid_test_data) < 2:
            raise ValueError("valid_test_data should be a list with at least two test cases for this test to work")
        for i, test_case in enumerate(valid_test_data):
            input_data = test_case.input_data

            result = characteristic.parse_value(input_data)

            # Should succeed without field errors
            case_desc = f"Test case {i + 1} ({test_case.description})"
            assert not result.field_errors, (
                f"{case_desc}: Valid data should parse without errors: {result.field_errors}"
            )
            assert result.parse_success, f"{case_desc}: parse_success should be True for valid data"
            assert result.value is not None, f"{case_desc}: Parsed value should not be None for valid data"
            assert result.characteristic.info.uuid == characteristic.uuid, (
                f"{case_desc}: Result info should match characteristic"
            )

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

    # === Dependency Tests ===
    def test_dependency_declarations_have_tests(
        self,
        characteristic: BaseCharacteristic,
        dependency_test_data: list[DependencyTestData] | None,
    ) -> None:
        """Verify that characteristics with dependencies have dependency tests.

        This test ensures that if a characteristic declares required or optional dependencies,
        the test class MUST provide dependency_test_data fixture with appropriate test cases.

        Why this matters:
        - Dependencies affect parsing order (topological sort in translator)
        - Dependencies enable cross-characteristic validation
        - Missing dependency tests = untested critical functionality
        """
        has_dependencies = bool(characteristic.required_dependencies or characteristic.optional_dependencies)

        if has_dependencies:
            # Characteristic declares dependencies - MUST have tests
            assert dependency_test_data is not None, (
                f"\n{'=' * 80}\n"
                f"TEST COVERAGE FAILURE: {type(characteristic).__name__} declares dependencies "
                f"but has no dependency tests!\n"
                f"\n"
                f"Required dependencies: {characteristic.required_dependencies}\n"
                f"Optional dependencies: {characteristic.optional_dependencies}\n"
                f"\n"
                f"ACTION REQUIRED: Add dependency_test_data fixture to your test class:\n"
                f"\n"
                f"@pytest.fixture\n"
                f"def dependency_test_data(self) -> list[DependencyTestData]:\n"
                f"    return [\n"
                f"        DependencyTestData(\n"
                f"            with_dependency_data={{\n"
                f"                '<measurement_uuid>': bytearray([...]),  # This characteristic's data\n"
                f"                '<dependency_uuid>': bytearray([...]),   # Dependency characteristic data\n"
                f"            }},\n"
                f"            without_dependency_data=bytearray([...]),   # Same data, no dependency\n"
                f"            expected_with=<expected_result>,            # Expected when dependency present\n"
                f"            expected_without=<expected_result>,         # Expected when dependency absent\n"
                f"            description='Test scenario description',\n"
                f"        ),\n"
                f"        # Add more test cases as needed\n"
                f"    ]\n"
                f"\n"
                f"See test_characteristic_dependencies.py for working examples (RSC, CSC).\n"
                f"{'=' * 80}\n"
            )

            assert len(dependency_test_data) > 0, (
                f"{type(characteristic).__name__} has dependencies but dependency_test_data is empty. "
                f"Provide at least one test case for dependency validation."
            )
        else:
            # No dependencies declared - dependency tests optional
            if dependency_test_data is not None:
                pytest.skip(f"{type(characteristic).__name__} has no dependencies, skipping dependency tests")

    def test_dependency_parsing_with_dependencies_present(
        self,
        characteristic: BaseCharacteristic,
        dependency_test_data: list[DependencyTestData] | None,
    ) -> None:
        """Test characteristic parsing when dependencies are present in context.

        This verifies:
        1. Characteristic parses successfully with dependencies
        2. Cross-validation with dependencies works correctly
        3. Context is properly utilized during parsing

        Note: This is a simplified test that passes raw bytes in context.
        For full integration testing with proper CharacteristicData objects,
        use tests/integration/test_characteristic_dependencies.py with translator.
        """
        if dependency_test_data is None:
            pytest.skip("No dependency test data provided")

        for i, test_case in enumerate(dependency_test_data):
            case_desc = f"Test case {i + 1} ({test_case.description})"

            # Get this characteristic's UUID and data
            char_uuid = str(characteristic.uuid).upper()
            char_data = test_case.with_dependency_data.get(char_uuid)

            if char_data is None:
                # Try to find by matching any key
                matching_keys = [k for k in test_case.with_dependency_data.keys() if k.upper() == char_uuid]
                if matching_keys:
                    char_data = test_case.with_dependency_data[matching_keys[0]]
                else:
                    pytest.fail(
                        f"{case_desc}: with_dependency_data must include data for this characteristic "
                        f"(UUID: {char_uuid})"
                    )

            # Build context with other characteristics (dependencies)
            # Parse dependency characteristics through their proper parsers to get CharacteristicData objects
            other_chars: dict[str, CharacteristicDataProtocol] = {}
            for dep_uuid, dep_data in test_case.with_dependency_data.items():
                if dep_uuid.upper() == char_uuid:
                    continue  # Skip the main characteristic

                # Get the characteristic class for this UUID and parse the data
                dep_char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(dep_uuid)
                if dep_char_class:
                    dep_instance = dep_char_class()
                    dep_parsed = dep_instance.parse_value(dep_data)
                    other_chars[dep_uuid] = dep_parsed
                else:
                    # If we can't find the class, skip this dependency
                    # (this shouldn't happen in well-formed tests)
                    continue

            ctx = CharacteristicContext(other_characteristics=other_chars) if other_chars else None

            # Parse with context
            result = characteristic.decode_value(char_data, ctx=ctx)

            # Should parse successfully and match expected value
            assert result is not None, f"{case_desc}: decode_value returned None when dependencies present"
            self._assert_values_equal(result, test_case.expected_with, f"{case_desc} with dependencies")

    def test_dependency_parsing_without_dependencies(
        self,
        characteristic: BaseCharacteristic,
        dependency_test_data: list[DependencyTestData] | None,
    ) -> None:
        """Test characteristic parsing when optional dependencies are absent.

        This verifies:
        1. Optional dependencies don't break parsing when absent
        2. Required dependencies (if any) properly fail or degrade gracefully
        3. Characteristic handles missing context appropriately
        """
        if dependency_test_data is None:
            pytest.skip("No dependency test data provided")

        has_required = bool(characteristic.required_dependencies)

        for i, test_case in enumerate(dependency_test_data):
            case_desc = f"Test case {i + 1} ({test_case.description})"

            # Parse without context (no dependencies available)
            if has_required:
                # Required dependencies missing - might fail or degrade
                if test_case.expected_without is None:
                    # Test expects failure - use broad exception since different characteristics
                    # may raise different exceptions (InsufficientDataError, ValueRangeError, etc.)
                    with pytest.raises(Exception):  # noqa: B017
                        characteristic.decode_value(test_case.without_dependency_data, ctx=None)
                else:
                    # Test expects degraded parsing (still works but limited)
                    result = characteristic.decode_value(test_case.without_dependency_data, ctx=None)
                    self._assert_values_equal(result, test_case.expected_without, f"{case_desc} without dependencies")
            else:
                # Only optional dependencies - should always work
                result = characteristic.decode_value(test_case.without_dependency_data, ctx=None)
                assert result is not None, f"{case_desc}: Should parse without optional dependencies"
                self._assert_values_equal(result, test_case.expected_without, f"{case_desc} without dependencies")

    def test_dependency_uuids_are_valid(
        self,
        characteristic: BaseCharacteristic,
    ) -> None:
        """Verify that declared dependency UUIDs are valid and resolvable.

        This catches typos in dependency declarations and ensures dependencies
        reference real characteristics.
        """
        all_deps = characteristic.required_dependencies + characteristic.optional_dependencies

        for dep_uuid in all_deps:
            # UUID should be properly formatted
            assert dep_uuid, "Dependency UUID cannot be empty"
            assert len(dep_uuid) >= 4, f"Dependency UUID '{dep_uuid}' is too short"

            # Should be hex string (allowing hyphens for full UUIDs)
            cleaned = dep_uuid.replace("-", "")
            assert all(c in "0123456789ABCDEFabcdef" for c in cleaned), (
                f"Dependency UUID '{dep_uuid}' contains invalid characters"
            )


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
