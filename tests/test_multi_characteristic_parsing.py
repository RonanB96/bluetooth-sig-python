"""Test multi-characteristic parsing with dependencies.

This module tests the multi-characteristic parsing pattern where one characteristic
depends on data from other characteristics, as specified in Bluetooth SIG specifications
(e.g., Glucose Measurement Context depends on Glucose Measurement for sequence number matching).
"""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.core import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics.base import CustomBaseCharacteristic
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.gatt_enums import GattProperty, ValueType
from bluetooth_sig.types.uuid import BluetoothUUID


class CalibrationCharacteristic(CustomBaseCharacteristic):
    """Example calibration characteristic (independent)."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("CA11B001-0000-1000-8000-00805F9B34FB"),
        name="Calibration Factor",
        unit="unitless",
        value_type=ValueType.FLOAT,
        properties=[GattProperty.READ],
    )

    min_length = 4
    expected_type = float

    def decode_value(self, data: bytearray, ctx: Any | None = None) -> float:
        """Parse calibration factor as float32.

        This characteristic is independent and does not use context.
        """
        import struct

        return struct.unpack("<f", bytes(data))[0]

    def encode_value(self, data: float) -> bytearray:
        """Encode calibration factor."""
        import struct

        return bytearray(struct.pack("<f", data))


class SensorReadingCharacteristic(CustomBaseCharacteristic):
    """Example sensor reading that depends on calibration (dependent).

    SIG Specification Pattern:
    This characteristic demonstrates the multi-characteristic dependency pattern
    where a measurement depends on calibration data from another characteristic.
    Similar to how Glucose Measurement Context uses sequence numbers to pair with
    Glucose Measurement data.
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("5E450001-0000-1000-8000-00805F9B34FB"),
        name="Sensor Reading",
        unit="calibrated units",
        value_type=ValueType.FLOAT,
        properties=[GattProperty.READ, GattProperty.NOTIFY],
    )

    # Declare dependency on calibration characteristic
    dependencies = ["CA11B001-0000-1000-8000-00805F9B34FB"]

    min_length = 2
    expected_type = float

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float:
        """Parse sensor reading and apply calibration if available.

        Args:
            data: Raw sensor reading as int16
            ctx: Optional context providing access to calibration characteristic

        Returns:
            Calibrated sensor reading (raw * calibration_factor)

        SIG Pattern:
        This demonstrates optional context enrichment - the characteristic works
        standalone but can be enhanced with context data when available.
        """
        # Parse raw sensor value
        raw_value = int.from_bytes(bytes(data[:2]), byteorder="little", signed=True)

        # Default calibration factor
        calibration_factor = 1.0

        # Enhance with context if available (SIG pattern: optional enrichment)
        if ctx is not None and ctx.other_characteristics:
            calib_char = ctx.other_characteristics.get("CA11B001-0000-1000-8000-00805F9B34FB")
            if calib_char and calib_char.parse_success:
                calibration_factor = calib_char.value
                # Note: In production, log when context is expected but missing

        return raw_value * calibration_factor

    def encode_value(self, data: float) -> bytearray:
        """Encode sensor reading (without calibration applied)."""
        # Encode as raw value
        raw = int(data)
        return bytearray(raw.to_bytes(2, byteorder="little", signed=True))


class SequenceNumberCharacteristic(CustomBaseCharacteristic):
    """Example characteristic with sequence number (independent)."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("5E900001-0000-1000-8000-00805F9B34FB"),
        name="Sequence Number",
        unit="",
        value_type=ValueType.INT,
        properties=[GattProperty.READ],
    )

    min_length = 2
    expected_type = int

    def decode_value(self, data: bytearray, ctx: Any | None = None) -> int:
        """Parse sequence number as uint16."""
        return int.from_bytes(bytes(data[:2]), byteorder="little", signed=False)

    def encode_value(self, data: int) -> bytearray:
        """Encode sequence number."""
        return bytearray(data.to_bytes(2, byteorder="little", signed=False))


class SequencedDataCharacteristic(CustomBaseCharacteristic):
    """Example characteristic that uses sequence number matching (dependent).

    SIG Pattern:
    This demonstrates the sequence number matching pattern used in
    Glucose Measurement Context and Blood Pressure services.
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("5E9DA7A1-0000-1000-8000-00805F9B34FB"),
        name="Sequenced Data",
        unit="various",
        value_type=ValueType.BYTES,
        properties=[GattProperty.READ, GattProperty.NOTIFY],
    )

    # Declare dependency on sequence number characteristic
    dependencies = ["5E900001-0000-1000-8000-00805F9B34FB"]

    min_length = 4
    expected_type = dict

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> dict[str, Any]:
        """Parse sequenced data with optional sequence number validation.

        SIG Pattern:
        Demonstrates sequence number matching for pairing related characteristics.
        """
        # Parse embedded sequence number and data value
        seq_num = int.from_bytes(bytes(data[:2]), byteorder="little", signed=False)
        data_value = int.from_bytes(bytes(data[2:4]), byteorder="little", signed=True)

        result: dict[str, Any] = {"sequence_number": seq_num, "value": data_value, "matched": False}

        # Match with context sequence number if available
        if ctx is not None and ctx.other_characteristics:
            seq_char = ctx.other_characteristics.get("5E900001-0000-1000-8000-00805F9B34FB")
            if seq_char and seq_char.parse_success:
                expected_seq = seq_char.value
                result["matched"] = seq_num == expected_seq

        return result

    def encode_value(self, data: dict[str, Any]) -> bytearray:
        """Encode sequenced data."""
        seq_num = data.get("sequence_number", 0)
        value = data.get("value", 0)
        return bytearray(
            seq_num.to_bytes(2, byteorder="little", signed=False) + value.to_bytes(2, byteorder="little", signed=True)
        )


class TestMultiCharacteristicDependencies:
    """Test suite for multi-characteristic parsing with dependencies."""

    @pytest.fixture
    def translator(self):
        """Create translator and register custom characteristics."""
        translator = BluetoothSIGTranslator()

        # Register custom characteristics (with override=True for test re-runs)
        translator.register_custom_characteristic_class(
            str(CalibrationCharacteristic._info.uuid),
            CalibrationCharacteristic,
            override=True,
        )
        translator.register_custom_characteristic_class(
            str(SensorReadingCharacteristic._info.uuid),
            SensorReadingCharacteristic,
            override=True,
        )
        translator.register_custom_characteristic_class(
            str(SequenceNumberCharacteristic._info.uuid),
            SequenceNumberCharacteristic,
            override=True,
        )
        translator.register_custom_characteristic_class(
            str(SequencedDataCharacteristic._info.uuid),
            SequencedDataCharacteristic,
            override=True,
        )

        return translator

    def test_dependency_declaration(self):
        """Test that characteristics can declare dependencies."""
        # Independent characteristic has no dependencies
        calib = CalibrationCharacteristic()
        assert calib.dependencies == []

        # Dependent characteristic declares its dependencies
        sensor = SensorReadingCharacteristic()
        assert sensor.dependencies == ["CA11B001-0000-1000-8000-00805F9B34FB"]

    def test_parse_independent_characteristic(self, translator):
        """Test parsing independent characteristic without context."""
        import struct

        # Create test data: calibration factor = 2.5
        calib_data = struct.pack("<f", 2.5)

        result = translator.parse_characteristic(
            str(CalibrationCharacteristic._info.uuid),
            calib_data,
        )

        assert result.parse_success is True
        assert result.value == pytest.approx(2.5)

    def test_parse_dependent_characteristic_without_context(self, translator):
        """Test that dependent characteristic works without context (standalone mode)."""
        # Create test data: raw sensor reading = 100
        sensor_data = (100).to_bytes(2, byteorder="little", signed=True)

        result = translator.parse_characteristic(
            str(SensorReadingCharacteristic._info.uuid),
            sensor_data,
        )

        assert result.parse_success is True
        # Without calibration context, uses default factor of 1.0
        assert result.value == pytest.approx(100.0)

    def test_parse_dependent_characteristic_with_context(self, translator):
        """Test that dependent characteristic uses context when available."""
        import struct

        # Create test data
        calib_data = struct.pack("<f", 2.5)
        sensor_data = (100).to_bytes(2, byteorder="little", signed=True)

        # Parse calibration first
        calib_result = translator.parse_characteristic(
            str(CalibrationCharacteristic._info.uuid),
            calib_data,
        )

        # Parse sensor with context containing calibration
        ctx = CharacteristicContext(other_characteristics={str(CalibrationCharacteristic._info.uuid): calib_result})

        sensor_result = translator.parse_characteristic(
            str(SensorReadingCharacteristic._info.uuid),
            sensor_data,
            ctx=ctx,
        )

        assert sensor_result.parse_success is True
        # With calibration context, applies factor: 100 * 2.5 = 250.0
        assert sensor_result.value == pytest.approx(250.0)

    def test_batch_parse_with_dependencies(self, translator):
        """Test that parse_characteristics handles dependencies automatically."""
        import struct

        # Create test data (order doesn't matter - will be sorted by dependencies)
        char_data = {
            # Dependent characteristic (will be parsed AFTER calibration)
            str(SensorReadingCharacteristic._info.uuid): (100).to_bytes(2, byteorder="little", signed=True),
            # Independent characteristic (will be parsed FIRST)
            str(CalibrationCharacteristic._info.uuid): struct.pack("<f", 2.5),
        }

        # Parse all characteristics in dependency order
        results = translator.parse_characteristics(char_data)

        # Both should parse successfully
        assert len(results) == 2
        assert all(r.parse_success for r in results.values())

        # Calibration should have default value
        calib_result = results[str(CalibrationCharacteristic._info.uuid)]
        assert calib_result.value == pytest.approx(2.5)

        # Sensor should use calibration from context (automatically provided)
        sensor_result = results[str(SensorReadingCharacteristic._info.uuid)]
        assert sensor_result.value == pytest.approx(250.0)

    def test_sequence_number_matching_pattern(self, translator):
        """Test sequence number matching pattern (SIG specification pattern)."""
        # Create test data with matching sequence numbers
        seq_data = (42).to_bytes(2, byteorder="little", signed=False)
        # Sequenced data: seq=42, value=123
        sequenced_data = (42).to_bytes(2, byteorder="little", signed=False) + (123).to_bytes(
            2, byteorder="little", signed=True
        )

        # Parse both characteristics
        results = translator.parse_characteristics(
            {
                str(SequenceNumberCharacteristic._info.uuid): seq_data,
                str(SequencedDataCharacteristic._info.uuid): sequenced_data,
            }
        )

        # Verify sequence number matching
        seq_result = results[str(SequenceNumberCharacteristic._info.uuid)]
        data_result = results[str(SequencedDataCharacteristic._info.uuid)]

        assert seq_result.parse_success is True
        assert seq_result.value == 42

        assert data_result.parse_success is True
        assert data_result.value["sequence_number"] == 42
        assert data_result.value["value"] == 123
        assert data_result.value["matched"] is True  # Sequence numbers match

    def test_sequence_number_mismatch(self, translator):
        """Test that sequence number mismatch is detected."""
        # Create test data with mismatched sequence numbers
        seq_data = (42).to_bytes(2, byteorder="little", signed=False)
        # Sequenced data: seq=99 (mismatch), value=123
        sequenced_data = (99).to_bytes(2, byteorder="little", signed=False) + (123).to_bytes(
            2, byteorder="little", signed=True
        )

        results = translator.parse_characteristics(
            {
                str(SequenceNumberCharacteristic._info.uuid): seq_data,
                str(SequencedDataCharacteristic._info.uuid): sequenced_data,
            }
        )

        data_result = results[str(SequencedDataCharacteristic._info.uuid)]
        assert data_result.parse_success is True
        assert data_result.value["matched"] is False  # Sequence numbers don't match

    def test_context_direct_access(self):
        """Test CharacteristicContext direct access to other_characteristics."""
        from bluetooth_sig.types import CharacteristicData

        # Create mock characteristic data
        calib_info = CharacteristicInfo(
            uuid=BluetoothUUID(str(CalibrationCharacteristic._info.uuid)),
            name="Calibration",
            unit="",
            value_type=ValueType.FLOAT,
            properties=[],
        )
        calib_data = CharacteristicData(
            info=calib_info,
            value=2.5,
            raw_data=b"\x00\x00\x20\x40",
        )

        # Create context
        ctx = CharacteristicContext(other_characteristics={str(CalibrationCharacteristic._info.uuid): calib_data})

        # Test direct access via other_characteristics
        assert ctx.other_characteristics is not None
        result = ctx.other_characteristics.get(str(CalibrationCharacteristic._info.uuid))
        assert result is not None
        assert result.value == 2.5

        # Test with non-existent UUID
        result = ctx.other_characteristics.get("nonexistent")
        assert result is None

        # Test getting all characteristics
        assert len(ctx.other_characteristics) == 1
        assert str(CalibrationCharacteristic._info.uuid) in ctx.other_characteristics

    def test_empty_context_access(self):
        """Test CharacteristicContext with empty other_characteristics."""
        ctx = CharacteristicContext()

        # Test that other_characteristics is None by default
        assert ctx.other_characteristics is None

    def test_circular_dependency_detection(self, translator):
        """Test that circular dependencies are detected and handled gracefully."""

        # Create characteristics with circular dependencies
        class CharA(CustomBaseCharacteristic):
            _info = CharacteristicInfo(
                uuid=BluetoothUUID("C4A1AAAA-0000-1000-8000-00805F9B34FB"),
                name="Char A",
                unit="",
                value_type=ValueType.INT,
                properties=[],
            )
            dependencies = ["C4A1BBBB-0000-1000-8000-00805F9B34FB"]

            def decode_value(self, data: bytearray, ctx: Any | None = None) -> int:
                return int(data[0])

            def encode_value(self, data: int) -> bytearray:
                return bytearray([data])

        class CharB(CustomBaseCharacteristic):
            _info = CharacteristicInfo(
                uuid=BluetoothUUID("C4A1BBBB-0000-1000-8000-00805F9B34FB"),
                name="Char B",
                unit="",
                value_type=ValueType.INT,
                properties=[],
            )
            dependencies = ["C4A1AAAA-0000-1000-8000-00805F9B34FB"]

            def decode_value(self, data: bytearray, ctx: Any | None = None) -> int:
                return int(data[0])

            def encode_value(self, data: int) -> bytearray:
                return bytearray([data])

        # Register characteristics
        translator.register_custom_characteristic_class(str(CharA._info.uuid), CharA)
        translator.register_custom_characteristic_class(str(CharB._info.uuid), CharB)

        # Try to parse with circular dependencies (should fall back to original order)
        char_data = {
            str(CharA._info.uuid): b"\x01",
            str(CharB._info.uuid): b"\x02",
        }

        # Should not raise error - falls back to original order
        results = translator.parse_characteristics(char_data)
        assert len(results) == 2
        assert all(r.parse_success for r in results.values())


class TestMultiCharacteristicExamples:
    """Additional examples demonstrating multi-characteristic patterns."""

    def test_readme_example(self):
        """Test example code suitable for README documentation."""
        # This example demonstrates the multi-characteristic parsing pattern

        translator = BluetoothSIGTranslator()

        # Register custom characteristics
        translator.register_custom_characteristic_class(
            str(CalibrationCharacteristic._info.uuid),
            CalibrationCharacteristic,
            override=True,
        )
        translator.register_custom_characteristic_class(
            str(SensorReadingCharacteristic._info.uuid),
            SensorReadingCharacteristic,
            override=True,
        )

        import struct

        # Prepare characteristic data
        char_data = {
            str(CalibrationCharacteristic._info.uuid): struct.pack("<f", 2.5),
            str(SensorReadingCharacteristic._info.uuid): (100).to_bytes(2, byteorder="little", signed=True),
        }

        # Parse all characteristics (dependencies handled automatically)
        results = translator.parse_characteristics(char_data)

        # Access parsed results
        sensor_result = results[str(SensorReadingCharacteristic._info.uuid)]
        assert sensor_result.value == pytest.approx(250.0)  # 100 * 2.5
