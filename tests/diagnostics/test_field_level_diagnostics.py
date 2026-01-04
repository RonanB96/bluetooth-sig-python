"""Tests for field-level parsing error diagnostics.

This module tests the new field-level error reporting and parse trace features
that provide actionable diagnostics when parsing fails.
"""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.gatt.characteristics.utils import DebugUtils
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.gatt.exceptions import ParseFieldError as ParseFieldException
from bluetooth_sig.types import CharacteristicInfo, ParseFieldError
from bluetooth_sig.types.gatt_enums import ValueType
from bluetooth_sig.types.uuid import BluetoothUUID


class MultiFieldCharacteristic(CustomBaseCharacteristic):
    """Test characteristic with multiple fields for field-level error testing."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("AAAAAAAA-1234-1234-1234-123456789012"),
        name="Multi Field Test",
        unit="various",
        value_type=ValueType.DICT,
    )

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> dict[str, Any]:
        """Decode multiple fields with explicit trace entries."""
        if len(data) < 4:
            # Raise ParseFieldException with field information
            raise ParseFieldException(
                characteristic="Multi Field Test",
                field="data_length",
                data=data,
                reason=f"need at least 4 bytes, got {len(data)}",
                offset=0,
            )

        # Parse flags byte (offset 0)
        flags = data[0]

        # Parse temperature (offset 1-2)
        temp_raw = int.from_bytes(data[1:3], byteorder="little", signed=True)
        if temp_raw < -1000 or temp_raw > 5000:
            raise ParseFieldException(
                characteristic="Multi Field Test",
                field="temperature",
                data=data[1:3],
                reason=f"value {temp_raw} out of valid range [-1000, 5000]",
                offset=1,
            )

        # Parse humidity (offset 3)
        humidity = data[3]
        if humidity > 100:
            raise ParseFieldException(
                characteristic="Multi Field Test",
                field="humidity",
                data=data[3:4],
                reason=f"value {humidity}% exceeds maximum 100%",
                offset=3,
            )

        return {
            "flags": flags,
            "temperature": temp_raw * 0.01,
            "humidity": humidity,
        }

    def _encode_value(self, data: dict[str, Any]) -> bytearray:
        """Encode multi-field data."""
        result = bytearray()
        result.append(data["flags"])
        temp_raw = int(data["temperature"] * 100)
        result.extend(temp_raw.to_bytes(2, byteorder="little", signed=True))
        result.append(data["humidity"])
        return result


class TestFieldLevelDiagnostics:
    """Test suite for field-level error reporting and parse traces."""

    def test_parse_success_includes_trace(self) -> None:
        """Test that successful parsing includes a parse trace."""
        char = MultiFieldCharacteristic()
        data = bytearray([0x01, 0xE8, 0x03, 50])  # flags=1, temp=10.00°C, humidity=50%

        result = char.parse_value(data)

        assert result.parse_success is True
        assert result.value is not None
        assert len(result.parse_trace) > 0
        assert "Starting parse" in result.parse_trace[0]
        assert "completed successfully" in result.parse_trace[-1]

    def test_field_error_in_temperature(self) -> None:
        """Test that temperature field errors are captured with field information."""
        char = MultiFieldCharacteristic()
        # Temperature value 6000 (0x1770) is out of range
        data = bytearray([0x01, 0x70, 0x17, 50])

        result = char.parse_value(data)

        assert result.parse_success is False
        assert result.value is None
        assert len(result.field_errors) == 1

        field_error = result.field_errors[0]
        assert field_error.field == "temperature"
        assert "out of valid range" in field_error.reason
        assert field_error.offset == 1

    def test_field_error_in_humidity(self) -> None:
        """Test that humidity field errors are captured with field information."""
        char = MultiFieldCharacteristic()
        # Humidity value 150 exceeds maximum 100
        data = bytearray([0x01, 0xE8, 0x03, 150])

        result = char.parse_value(data)

        assert result.parse_success is False
        assert result.value is None
        assert len(result.field_errors) == 1

        field_error = result.field_errors[0]
        assert field_error.field == "humidity"
        assert "exceeds maximum 100%" in field_error.reason
        assert field_error.offset == 3

    def test_field_error_in_data_length(self) -> None:
        """Test that insufficient data errors are captured as field errors."""
        char = MultiFieldCharacteristic()
        data = bytearray([0x01, 0xE8])  # Only 2 bytes, need 4

        result = char.parse_value(data)

        assert result.parse_success is False
        assert result.value is None
        assert len(result.field_errors) == 1

        field_error = result.field_errors[0]
        assert field_error.field == "data_length"
        assert "need at least 4 bytes" in field_error.reason
        assert field_error.offset == 0

    def test_parse_trace_on_failure(self) -> None:
        """Test that parse trace captures steps leading to failure."""
        char = MultiFieldCharacteristic()
        data = bytearray([0x01, 0x70, 0x17, 50])  # Temperature out of range

        result = char.parse_value(data)

        assert result.parse_success is False
        assert len(result.parse_trace) > 0
        assert any("Starting parse" in step for step in result.parse_trace)
        assert any("Field error" in step for step in result.parse_trace)

    def test_debug_utils_format_field_error(self) -> None:
        """Test DebugUtils.format_field_error produces readable output."""
        error = ParseFieldError(
            field="temperature",
            reason="value 6000 out of valid range [-1000, 5000]",
            offset=1,
            raw_slice=bytes([0x70, 0x17]),
        )
        data = bytearray([0x01, 0x70, 0x17, 50])

        formatted = DebugUtils.format_field_error(error, data)

        assert "temperature" in formatted
        assert "value 6000 out of valid range" in formatted
        assert "Offset: 1" in formatted
        assert "70 17" in formatted  # Hex dump

    def test_debug_utils_format_field_errors(self) -> None:
        """Test DebugUtils.format_field_errors handles multiple errors."""
        errors = [
            ParseFieldError(
                field="temperature",
                reason="out of range",
                offset=1,
                raw_slice=None,
            ),
            ParseFieldError(
                field="humidity",
                reason="exceeds maximum",
                offset=3,
                raw_slice=None,
            ),
        ]
        data = bytearray([0x01, 0x70, 0x17, 150])

        formatted = DebugUtils.format_field_errors(errors, data)

        assert "Found 2 field error(s)" in formatted
        assert "temperature" in formatted
        assert "humidity" in formatted

    def test_debug_utils_format_parse_trace(self) -> None:
        """Test DebugUtils.format_parse_trace produces readable output."""
        trace = [
            "Starting parse of Multi Field Test",
            "Validating data length (got 4 bytes)",
            "Decoding value",
            "Field error in 'temperature': value out of range",
        ]

        formatted = DebugUtils.format_parse_trace(trace)

        assert "Parse trace:" in formatted
        assert all(step in formatted for step in trace)

    def test_field_error_includes_hex_context(self) -> None:
        """Test that field errors include hex dump context for debugging."""
        char = MultiFieldCharacteristic()
        data = bytearray([0x01, 0x70, 0x17, 50])

        result = char.parse_value(data)

        assert result.parse_success is False
        assert len(result.field_errors) == 1

        # Format the error for display
        formatted = DebugUtils.format_field_error(result.field_errors[0], data)

        # Should include hex representation
        assert "70" in formatted or "17" in formatted

    def test_error_message_backward_compatibility(self) -> None:
        """Test that error_message field is still populated for backward compatibility."""
        char = MultiFieldCharacteristic()
        data = bytearray([0x01, 0x70, 0x17, 50])

        result = char.parse_value(data)

        assert result.parse_success is False
        assert result.error_message != ""
        assert "temperature" in result.error_message

    def test_empty_field_errors_on_success(self) -> None:
        """Test that successful parsing has empty field_errors list."""
        char = MultiFieldCharacteristic()
        data = bytearray([0x01, 0xE8, 0x03, 50])

        result = char.parse_value(data)

        assert result.parse_success is True
        assert result.field_errors == []

    def test_raw_slice_in_field_error(self) -> None:
        """Test that ParseFieldException captures raw data slice."""
        char = MultiFieldCharacteristic()
        data = bytearray([0x01, 0x70, 0x17, 150])  # Humidity out of range

        result = char.parse_value(data)

        assert result.parse_success is False
        assert len(result.field_errors) == 1
        assert result.field_errors[0].raw_slice is not None


class TestGenericErrorExtraction:
    """Test suite for extracting field information from generic exceptions."""

    def test_generic_value_error_extraction(self) -> None:
        """Test that generic ValueError messages do not produce field errors.

        Generic errors (not ParseFieldException) are reported in the main
        error_message field but do not produce field_errors entries.
        """

        class GenericErrorCharacteristic(CustomBaseCharacteristic):
            _info = CharacteristicInfo(
                uuid=BluetoothUUID("BBBBBBBB-1234-1234-1234-123456789012"),
                name="Generic Error Test",
                unit="",
                value_type=ValueType.INT,
            )

            expected_type: type | None = int
            min_value: int | float | None = 0
            max_value: int | float | None = 100

            def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
                """Return value that will fail validation."""
                return 200  # Out of range

            def _encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = GenericErrorCharacteristic()
        data = bytearray([0xC8])

        result = char.parse_value(data)

        assert result.parse_success is False
        # Generic errors do not produce field_errors (no brittle string parsing)
        assert len(result.field_errors) == 0
        # But the error message is still captured
        assert "Value 200 is above maximum 100" in result.error_message
        assert "Parse failed:" in result.parse_trace[-1]


class TestFieldErrorFormatting:
    """Test suite for field error formatting utilities."""

    def test_format_field_error_with_offset(self) -> None:
        """Test formatting field error with offset information."""
        error = ParseFieldError(
            field="flags",
            reason="invalid bit combination",
            offset=0,
            raw_slice=bytes([0xFF]),
        )
        data = bytearray([0xFF, 0x00, 0x10, 0x32])

        formatted = DebugUtils.format_field_error(error, data)

        assert "flags" in formatted
        assert "Offset: 0" in formatted
        assert "FF" in formatted

    def test_format_field_error_without_offset(self) -> None:
        """Test formatting field error without offset information."""
        error = ParseFieldError(
            field="overall_structure",
            reason="malformed data",
            offset=None,
            raw_slice=None,
        )
        data = bytearray([0x01, 0x02, 0x03])

        formatted = DebugUtils.format_field_error(error, data)

        assert "overall_structure" in formatted
        assert "malformed data" in formatted
        # Should show full data when offset not available
        assert "01 02 03" in formatted

    def test_empty_field_errors_formatting(self) -> None:
        """Test formatting empty field errors list."""
        formatted = DebugUtils.format_field_errors([], bytearray())

        assert "No field errors" in formatted

    def test_empty_parse_trace_formatting(self) -> None:
        """Test formatting empty parse trace."""
        formatted = DebugUtils.format_parse_trace([])

        assert "No parse trace available" in formatted


class TestTraceControlPerformance:
    """Test suite for parse trace control performance feature."""

    def test_trace_disabled_for_performance(self) -> None:
        """Test that parse trace can be disabled for performance."""

        class NoTraceCharacteristic(CustomBaseCharacteristic):
            """Characteristic with trace disabled."""

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("FFFFFFFF-1234-1234-1234-123456789012"),
                name="No Trace Test",
                unit="test",
                value_type=ValueType.INT,
            )

            # Disable trace collection for performance
            _enable_parse_trace = False

            def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
                """Simple decode."""
                return int(data[0])

            def _encode_value(self, data: int) -> bytearray:
                """Simple encode."""
                return bytearray([data])

        char = NoTraceCharacteristic()
        data = bytearray([42])

        result = char.parse_value(data)

        # Parse should succeed
        assert result.parse_success is True
        assert result.value == 42

        # But trace should be empty due to disabled flag
        assert len(result.parse_trace) == 0

    def test_trace_enabled_by_default(self) -> None:
        """Test that parse trace is enabled by default."""

        class DefaultTraceCharacteristic(CustomBaseCharacteristic):
            """Characteristic with default trace setting."""

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("EEEEEEEE-1234-1234-1234-123456789012"),
                name="Default Trace Test",
                unit="test",
                value_type=ValueType.INT,
            )

            # Don't set _enable_parse_trace - should default to True

            def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
                """Simple decode."""
                return int(data[0])

            def _encode_value(self, data: int) -> bytearray:
                """Simple encode."""
                return bytearray([data])

        char = DefaultTraceCharacteristic()
        data = bytearray([42])

        result = char.parse_value(data)

        # Parse should succeed
        assert result.parse_success is True
        assert result.value == 42

        # Trace should have entries by default
        assert len(result.parse_trace) > 0

    def test_trace_disabled_via_environment_variable(self) -> None:
        """Test that parse trace can be disabled via environment variable."""
        import os

        class EnvTraceCharacteristic(CustomBaseCharacteristic):
            _info = CharacteristicInfo(
                uuid=BluetoothUUID("EEEEEEEE-1234-1234-1234-123456789012"),
                name="Environment Trace Test",
                unit="",
                value_type=ValueType.INT,
            )

            def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
                """Simple decode."""
                return int(data[0])

            def _encode_value(self, data: int) -> bytearray:
                """Simple encode."""
                return bytearray([data])

        # Set environment variable to disable tracing
        old_value = os.environ.get("BLUETOOTH_SIG_ENABLE_PARSE_TRACE")
        try:
            os.environ["BLUETOOTH_SIG_ENABLE_PARSE_TRACE"] = "0"

            char = EnvTraceCharacteristic()
            data = bytearray([42])

            result = char.parse_value(data)

            # Parse should succeed
            assert result.parse_success is True
            assert result.value == 42

            # Trace should be empty when disabled via env var
            assert len(result.parse_trace) == 0
        finally:
            # Restore original environment
            if old_value is None:
                os.environ.pop("BLUETOOTH_SIG_ENABLE_PARSE_TRACE", None)
            else:
                os.environ["BLUETOOTH_SIG_ENABLE_PARSE_TRACE"] = old_value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
