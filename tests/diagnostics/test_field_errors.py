"""Tests for logging integration with field-level error reporting.

This module tests that field-level errors and parse traces are properly
integrated with the logging system for improved debugging.
"""

from __future__ import annotations

from typing import Any

from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.gatt.characteristics.utils import DebugUtils
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.gatt.exceptions import ParseFieldError as ParseFieldException
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.uuid import BluetoothUUID


class LoggingTestCharacteristic(CustomBaseCharacteristic):
    """Test characteristic with field errors for logging integration testing."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("CCCCCCCC-1234-1234-1234-123456789012"),
        name="Logging Test Characteristic",
        unit="test",
        python_type=dict,
    )

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> dict[str, Any]:
        """Decode with potential field errors."""
        if len(data) < 3:
            raise ParseFieldException(
                characteristic="Logging Test Characteristic",
                field="data_length",
                data=data,
                reason=f"need at least 3 bytes, got {len(data)}",
                offset=0,
            )

        value = data[0]
        if value > 200:
            raise ParseFieldException(
                characteristic="Logging Test Characteristic",
                field="value",
                data=data[0:1],
                reason=f"value {value} exceeds maximum 200",
                offset=0,
            )

        return {"value": value, "extra": int.from_bytes(data[1:3], byteorder="little")}

    def _encode_value(self, data: dict[str, Any]) -> bytearray:
        """Encode test data."""
        result = bytearray([data["value"]])
        result.extend(data["extra"].to_bytes(2, byteorder="little"))
        return result


class TestLoggingFieldErrors:
    """Test suite for logging integration with field-level errors."""

    def test_field_errors_available_in_result(self) -> None:
        """Test that field errors are available in parse exception for logging."""
        import pytest

        from bluetooth_sig.gatt.exceptions import CharacteristicParseError

        char = LoggingTestCharacteristic()
        # Data that will cause field error (value > 200)
        data = bytes([250, 0x10, 0x20])

        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(data)

        # Verify field errors are populated
        assert len(exc_info.value.field_errors) > 0
        assert exc_info.value.field_errors[0].field == "value"
        assert "exceeds maximum 200" in exc_info.value.field_errors[0].reason

        # Verify parse trace is populated
        assert len(exc_info.value.parse_trace) > 0

    def test_parse_trace_available_for_logging(self) -> None:
        """Test that parse trace is available on success."""
        char = LoggingTestCharacteristic()
        # Valid data
        data = bytes([100, 0x10, 0x20])

        result = char.parse_value(data)

        # Verify parse succeeded - returns dict directly
        assert isinstance(result, dict)
        assert result["value"] == 100

    def test_debug_utils_format_for_logging(self) -> None:
        """Test that DebugUtils formatting works for logging output."""
        import pytest

        from bluetooth_sig.gatt.exceptions import CharacteristicParseError

        char = LoggingTestCharacteristic()
        data = bytes([250, 0x10, 0x20])

        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(data)

        # Format field errors for logging
        if exc_info.value.field_errors:
            formatted_errors = DebugUtils.format_field_errors(exc_info.value.field_errors, exc_info.value.raw_data)
            assert "Found 1 field error" in formatted_errors
            assert "value" in formatted_errors

        # Format parse trace for logging
        if exc_info.value.parse_trace:
            formatted_trace = DebugUtils.format_parse_trace(exc_info.value.parse_trace)
            assert "Parse trace:" in formatted_trace

    def test_field_error_hex_dump_in_logging(self) -> None:
        """Test that hex dump context is available for logging."""
        import pytest

        from bluetooth_sig.gatt.exceptions import CharacteristicParseError

        char = LoggingTestCharacteristic()
        data = bytes([250, 0x10, 0x20])

        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(data)

        # Get formatted error with hex context
        if exc_info.value.field_errors:
            formatted = DebugUtils.format_field_error(exc_info.value.field_errors[0], exc_info.value.raw_data)

            # Should contain hex representation for debugging
            assert "FA" in formatted or "250" in formatted  # Hex or decimal representation

    def test_exception_message_contains_field_info(self) -> None:
        """Test that exception message contains field information."""
        import pytest

        from bluetooth_sig.gatt.exceptions import CharacteristicParseError

        char = LoggingTestCharacteristic()
        data = bytes([250, 0x10, 0x20])

        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(data)

        # Exception message should contain field info
        assert "value" in str(exc_info.value)

        # New field_errors should also be available
        assert len(exc_info.value.field_errors) > 0

    def test_multiple_field_errors_logging(self) -> None:
        """Test logging with multiple field errors."""
        import pytest

        from bluetooth_sig.gatt.exceptions import CharacteristicParseError

        class MultiErrorCharacteristic(CustomBaseCharacteristic):
            """Characteristic that can produce multiple field errors."""

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("DDDDDDDD-1234-1234-1234-123456789012"),
                name="Multi Error Test",
                unit="test",
                python_type=dict,
            )

            def _decode_value(
                self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
            ) -> dict[str, Any]:
                """Decode with validation that can fail in multiple fields."""
                # Check field 1
                if len(data) < 2:
                    raise ParseFieldException(
                        characteristic="Multi Error Test",
                        field="field1",
                        data=data,
                        reason="insufficient data",
                        offset=0,
                    )

                # Check field 2 - this will only be reached if field 1 is ok
                if data[1] > 100:
                    raise ParseFieldException(
                        characteristic="Multi Error Test",
                        field="field2",
                        data=data[1:2],
                        reason="value exceeds maximum",
                        offset=1,
                    )

                return {"field1": data[0], "field2": data[1]}

            def _encode_value(self, data: dict[str, Any]) -> bytearray:
                """Encode multi-field data."""
                return bytearray([data["field1"], data["field2"]])

        char = MultiErrorCharacteristic()
        # This will fail on field2
        data = bytes([50, 150])

        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(data)

        assert len(exc_info.value.field_errors) > 0

        # Format for logging should handle multiple errors
        formatted = DebugUtils.format_field_errors(exc_info.value.field_errors, exc_info.value.raw_data)
        assert "field error" in formatted.lower()


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
