"""Test multi-characteristic parsing with dependencies.

This module tests the multi-characteristic parsing pattern where one characteristic
depends on data from other characteristics, as specified in Bluetooth SIG specifications
(e.g., Glucose Measurement Context depends on Glucose Measurement for sequence number matching).
"""

from __future__ import annotations

from typing import Any, ClassVar

import pytest

from bluetooth_sig.core import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.gatt_enums import ValueType
from bluetooth_sig.types.units import PressureUnit
from bluetooth_sig.types.uuid import BluetoothUUID


def characteristic_uuid(characteristic_cls: type[CustomBaseCharacteristic]) -> str:
    """Return the string UUID for the given characteristic class."""
    return str(characteristic_cls().info.uuid)


class CalibrationCharacteristic(CustomBaseCharacteristic):
    """Example calibration characteristic (independent)."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("CA11B001-0000-1000-8000-00805F9B34FB"),
        name="Calibration Factor",
        unit="unitless",
        value_type=ValueType.FLOAT,
    )

    min_length = 4
    expected_type = float

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> float:
        """Parse calibration factor as float32.

        This characteristic is independent and does not use context.
        """
        import struct
        from typing import cast

        return cast("float", struct.unpack("<f", bytes(data))[0])

    def _encode_value(self, data: float) -> bytearray:
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
    )

    # Reference calibration directly (no hardcoded UUIDs)
    _required_dependencies: ClassVar[list[type]] = [CalibrationCharacteristic]

    min_length = 2
    expected_type = float

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> float:
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
            calib_value = ctx.other_characteristics.get("CA11B001-0000-1000-8000-00805F9B34FB")
            if calib_value is not None:
                calibration_factor = calib_value
                # Note: In production, log when context is expected but missing

        return raw_value * calibration_factor

    def _encode_value(self, data: float) -> bytearray:
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
    )

    min_length = 2
    expected_type = int

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> int:
        """Parse sequence number as uint16."""
        return int.from_bytes(bytes(data[:2]), byteorder="little", signed=False)

    def _encode_value(self, data: int) -> bytearray:
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
    )

    # Declare dependency using direct class reference (following Django ForeignKey pattern)

    _required_dependencies: ClassVar[list[type]] = [SequenceNumberCharacteristic]

    min_length = 4
    expected_type = dict

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> dict[str, Any]:
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
            expected_seq = ctx.other_characteristics.get("5E900001-0000-1000-8000-00805F9B34FB")
            if expected_seq is not None:
                result["matched"] = seq_num == expected_seq

        return result

    def _encode_value(self, data: dict[str, Any]) -> bytearray:
        """Encode sequenced data."""
        seq_num = data.get("sequence_number", 0)
        value = data.get("value", 0)
        return bytearray(
            seq_num.to_bytes(2, byteorder="little", signed=False) + value.to_bytes(2, byteorder="little", signed=True)
        )


CALIBRATION_UUID = characteristic_uuid(CalibrationCharacteristic)
SENSOR_READING_UUID = characteristic_uuid(SensorReadingCharacteristic)
SEQUENCE_NUMBER_UUID = characteristic_uuid(SequenceNumberCharacteristic)
SEQUENCED_DATA_UUID = characteristic_uuid(SequencedDataCharacteristic)


class TestMultiCharacteristicDependencies:
    """Test suite for multi-characteristic parsing with dependencies."""

    @pytest.fixture
    def translator(self) -> BluetoothSIGTranslator:
        """Create translator and register custom characteristics."""
        translator = BluetoothSIGTranslator()

        # Register custom characteristics (with override=True for test re-runs)
        translator.register_custom_characteristic_class(
            CALIBRATION_UUID,
            CalibrationCharacteristic,
            override=True,
        )
        translator.register_custom_characteristic_class(
            SENSOR_READING_UUID,
            SensorReadingCharacteristic,
            override=True,
        )
        translator.register_custom_characteristic_class(
            SEQUENCE_NUMBER_UUID,
            SequenceNumberCharacteristic,
            override=True,
        )
        translator.register_custom_characteristic_class(
            SEQUENCED_DATA_UUID,
            SequencedDataCharacteristic,
            override=True,
        )

        return translator

    def test_dependency_declaration(self) -> None:
        """Test that characteristics can declare dependencies with hard types."""
        # Independent characteristic has no dependencies
        calib = CalibrationCharacteristic()
        assert calib.required_dependencies == []

        # Dependent characteristic declares its dependencies using direct class reference
        sensor = SensorReadingCharacteristic()
        assert sensor.required_dependencies == [CALIBRATION_UUID]

    def test_parse_independent_characteristic(self, translator: BluetoothSIGTranslator) -> None:
        """Test parsing independent characteristic without context."""
        import struct

        calib_data = struct.pack("<f", 2.5)

        result = translator.parse_characteristic(CALIBRATION_UUID, calib_data)

        assert result == pytest.approx(2.5)

    def test_parse_dependent_characteristic_without_context(self, translator: BluetoothSIGTranslator) -> None:
        """Test that dependent characteristic works without context (standalone mode)."""
        sensor_data = (100).to_bytes(2, byteorder="little", signed=True)

        result = translator.parse_characteristic(SENSOR_READING_UUID, sensor_data)

        assert result == pytest.approx(100.0)

    def test_parse_dependent_characteristic_with_context(self, translator: BluetoothSIGTranslator) -> None:
        """Test that dependent characteristic uses context when available."""
        import struct

        calib_data = struct.pack("<f", 2.5)
        sensor_data = (100).to_bytes(2, byteorder="little", signed=True)

        # Parse calibration first to get its value
        calib_result = translator.parse_characteristic(CALIBRATION_UUID, calib_data)

        # Context now stores raw parsed values directly
        context_map: dict[str, Any] = {
            CALIBRATION_UUID: calib_result,
        }
        ctx = CharacteristicContext(other_characteristics=context_map)

        sensor_result = translator.parse_characteristic(
            SENSOR_READING_UUID,
            sensor_data,
            ctx=ctx,
        )

        # 100 * 2.5 = 250.0
        assert sensor_result == pytest.approx(250.0)

    def test_batch_parse_with_dependencies(self, translator: BluetoothSIGTranslator) -> None:
        """Test that parse_characteristics handles dependencies automatically."""
        import struct

        # Create test data (order doesn't matter - will be sorted by dependencies)
        char_data = {
            # Dependent characteristic (will be parsed AFTER calibration)
            SENSOR_READING_UUID: (100).to_bytes(2, byteorder="little", signed=True),
            # Independent characteristic (will be parsed FIRST)
            CALIBRATION_UUID: struct.pack("<f", 2.5),
        }

        # Parse all characteristics in dependency order
        results: dict[str, Any] = translator.parse_characteristics(char_data)

        # Both should parse successfully (results returned, not CharacteristicData)
        assert len(results) == 2

        # Calibration should have the float value
        calib_result = results[CALIBRATION_UUID]
        assert calib_result == pytest.approx(2.5)

        # Sensor should use calibration from context (automatically provided)
        sensor_result = results[SENSOR_READING_UUID]
        assert sensor_result == pytest.approx(250.0)

    def test_missing_required_dependency_fails_fast(self, translator: BluetoothSIGTranslator) -> None:
        """Missing required dependency should raise MissingDependencyError."""
        from bluetooth_sig.gatt.exceptions import MissingDependencyError

        sensor_uuid = str(SensorReadingCharacteristic().info.uuid)
        raw_sensor = (100).to_bytes(2, byteorder="little", signed=True)

        # parse_characteristics now raises MissingDependencyError for missing required deps
        with pytest.raises(MissingDependencyError) as exc_info:
            translator.parse_characteristics({sensor_uuid: raw_sensor})

        # Verify the error message mentions the missing dependency
        assert "Sensor Reading" in str(exc_info.value) or "missing" in str(exc_info.value).lower()

    def test_optional_dependency_absent_still_succeeds(self, translator: BluetoothSIGTranslator) -> None:
        """Optional dependencies should not block parsing when unavailable."""
        from bluetooth_sig.gatt.characteristics.blood_pressure_measurement import (
            BloodPressureData,
            BloodPressureMeasurementCharacteristic,
        )

        bp_char = BloodPressureMeasurementCharacteristic()
        measurement = BloodPressureData(
            systolic=120.0,
            diastolic=80.0,
            mean_arterial_pressure=90.0,
            unit=PressureUnit.MMHG,
        )
        raw_bp = bytes(bp_char.build_value(measurement))
        bp_uuid = str(bp_char.info.uuid)

        results = translator.parse_characteristics({bp_uuid: raw_bp})

        assert bp_uuid in results
        bp_result = results[bp_uuid]
        assert isinstance(bp_result, BloodPressureData)

    def test_sequence_number_matching_pattern(self, translator: BluetoothSIGTranslator) -> None:
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

        assert seq_result == 42

        assert data_result is not None
        assert isinstance(data_result, dict)
        assert data_result["sequence_number"] == 42
        assert data_result["value"] == 123
        assert data_result["matched"] is True  # Sequence numbers match

    def test_sequence_number_mismatch(self, translator: BluetoothSIGTranslator) -> None:
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
        assert data_result is not None
        assert isinstance(data_result, dict)
        assert data_result["matched"] is False  # Sequence numbers don't match

    def test_context_direct_access(self) -> None:
        """Test CharacteristicContext direct access to other_characteristics."""
        # Context now stores raw parsed values directly
        calib_value = 2.5

        # Create context with raw value
        ctx = CharacteristicContext(other_characteristics={str(CalibrationCharacteristic._info.uuid): calib_value})

        # Test direct access via other_characteristics
        other_chars = ctx.other_characteristics
        assert other_chars is not None
        result = other_chars.get(str(CalibrationCharacteristic._info.uuid))
        assert result is not None
        assert result == 2.5

        # Test with non-existent UUID
        result = other_chars.get("nonexistent")
        assert result is None

        # Test getting all characteristics
        assert len(other_chars) == 1
        # Use .get() to verify presence as Mapping doesn't need 'in' operator
        assert other_chars.get(str(CalibrationCharacteristic._info.uuid)) is not None

    def test_empty_context_access(self) -> None:
        """Test CharacteristicContext with empty other_characteristics."""
        ctx = CharacteristicContext()

        # Test that other_characteristics is None by default
        assert ctx.other_characteristics is None

    def test_circular_dependency_detection(self, translator: BluetoothSIGTranslator) -> None:
        """Test that circular dependencies are detected and handled gracefully."""

        # Create characteristics with circular dependencies
        class CharA(CustomBaseCharacteristic):
            _info = CharacteristicInfo(
                uuid=BluetoothUUID("C4A1AAAA-0000-1000-8000-00805F9B34FB"),
                name="Char A",
                unit="",
                value_type=ValueType.INT,
            )
            # Forward reference will be resolved after CharB is defined
            _required_dependencies: ClassVar[list[type]] = []

            def _decode_value(
                self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
            ) -> int:
                return int(data[0])

            def _encode_value(self, data: int) -> bytearray:
                return bytearray([data])

        class CharB(CustomBaseCharacteristic):
            _info = CharacteristicInfo(
                uuid=BluetoothUUID("C4A1BBBB-0000-1000-8000-00805F9B34FB"),
                name="Char B",
                unit="",
                value_type=ValueType.INT,
            )
            # Reference CharA directly (no hardcoding)
            _required_dependencies: ClassVar[list[type]] = [CharA]

            def _decode_value(
                self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
            ) -> int:
                return int(data[0])

            def _encode_value(self, data: int) -> bytearray:
                return bytearray([data])

        # Complete circular reference (CharA depends on CharB)
        CharA._required_dependencies = [CharB]

        # Register characteristics
        translator.register_custom_characteristic_class(str(CharA._info.uuid), CharA)
        translator.register_custom_characteristic_class(str(CharB._info.uuid), CharB)

        # Try to parse with circular dependencies
        # Topological sort will fail, fallback to original order
        # Both will fail due to missing required dependencies (since each depends on the other)
        char_data = {
            str(CharA._info.uuid): b"\x01",
            str(CharB._info.uuid): b"\x02",
        }

        from bluetooth_sig.gatt.exceptions import MissingDependencyError

        with pytest.raises(MissingDependencyError):
            translator.parse_characteristics(char_data)


class TestMultiCharacteristicExamples:
    """Additional examples demonstrating multi-characteristic patterns."""

    def test_readme_example(self) -> None:
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
        assert sensor_result == pytest.approx(250.0)  # 100 * 2.5


class TestRequiredOptionalDependencies:
    """Test suite for required vs optional dependency handling."""

    @pytest.fixture
    def translator(self) -> BluetoothSIGTranslator:
        """Create translator and register characteristics for dependency testing."""
        translator = BluetoothSIGTranslator()

        # Define characteristic with REQUIRED dependency
        class MeasurementCharacteristic(CustomBaseCharacteristic):
            """Independent measurement characteristic."""

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("0EA50001-0000-1000-8000-00805F9B34FB"),
                name="Measurement",
                unit="units",
                value_type=ValueType.INT,
            )

            min_length = 2
            expected_type = int

            def _decode_value(
                self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
            ) -> int:
                return int.from_bytes(bytes(data[:2]), byteorder="little", signed=False)

            def _encode_value(self, data: int) -> bytearray:
                return bytearray(data.to_bytes(2, byteorder="little", signed=False))

        class ContextCharacteristic(CustomBaseCharacteristic):
            """Context that REQUIRES measurement."""

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("C0111E11-0000-1000-8000-00805F9B34FB"),
                name="Context",
                unit="various",
                value_type=ValueType.DICT,
            )

            _required_dependencies: ClassVar[list[type]] = [MeasurementCharacteristic]

            min_length = 2
            expected_type = dict

            def _decode_value(
                self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
            ) -> dict[str, Any]:
                value = int.from_bytes(bytes(data[:2]), byteorder="little", signed=False)
                result = {"context_value": value, "has_measurement": False}

                if ctx and ctx.other_characteristics:
                    meas = ctx.other_characteristics.get("0EA50001-0000-1000-8000-00805F9B34FB")
                    if meas is not None:
                        result["has_measurement"] = True
                        result["measurement_value"] = meas

                return result

            def _encode_value(self, data: dict[str, Any]) -> bytearray:
                return bytearray(data.get("context_value", 0).to_bytes(2, byteorder="little", signed=False))

        class EnrichmentCharacteristic(CustomBaseCharacteristic):
            """Optional enrichment characteristic."""

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("E111C401-0000-1000-8000-00805F9B34FB"),
                name="Enrichment",
                unit="factor",
                value_type=ValueType.FLOAT,
            )

            min_length = 4
            expected_type = float

            def _decode_value(
                self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
            ) -> float:
                import struct
                from typing import cast

                return cast("float", struct.unpack("<f", bytes(data[:4]))[0])

            def _encode_value(self, data: float) -> bytearray:
                import struct

                return bytearray(struct.pack("<f", data))

        class DataCharacteristic(CustomBaseCharacteristic):
            """Data that OPTIONALLY uses enrichment."""

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("DA1A0001-0000-1000-8000-00805F9B34FB"),
                name="Data",
                unit="various",
                value_type=ValueType.DICT,
            )

            _optional_dependencies: ClassVar[list[type]] = [EnrichmentCharacteristic]

            min_length = 2
            expected_type = dict

            def _decode_value(
                self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
            ) -> dict[str, Any]:
                value = int.from_bytes(bytes(data[:2]), byteorder="little", signed=False)
                result = {"data_value": value, "enriched": False}

                if ctx and ctx.other_characteristics:
                    enrich = ctx.other_characteristics.get("E111C401-0000-1000-8000-00805F9B34FB")
                    if enrich is not None:
                        result["enriched"] = True
                        result["enriched_value"] = value * enrich

                return result

            def _encode_value(self, data: dict[str, Any]) -> bytearray:
                return bytearray(data.get("data_value", 0).to_bytes(2, byteorder="little", signed=False))

        class MultiDependencyCharacteristic(CustomBaseCharacteristic):
            """Characteristic that combines required and optional dependencies."""

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("F0EADF11-0000-1000-8000-00805F9B34FB"),
                name="Multi Dependency",
                unit="composite",
                value_type=ValueType.DICT,
            )

            _required_dependencies: ClassVar[list[type]] = [
                MeasurementCharacteristic,
                ContextCharacteristic,
            ]
            _optional_dependencies: ClassVar[list[type]] = [EnrichmentCharacteristic]

            min_length = 4
            expected_type = dict

            def _decode_value(
                self,
                data: bytearray,
                ctx: CharacteristicContext | None = None,
                *,
                validate: bool = True,
            ) -> dict[str, Any]:
                measurement_ref = int.from_bytes(bytes(data[:2]), byteorder="little", signed=False)
                context_ref = int.from_bytes(bytes(data[2:4]), byteorder="little", signed=False)

                if ctx is None or ctx.other_characteristics is None:
                    raise ValueError("Multi Dependency characteristic requires parsed dependency context")

                measurement_uuid = str(MeasurementCharacteristic().info.uuid)
                context_uuid = str(ContextCharacteristic().info.uuid)
                optional_uuid = str(EnrichmentCharacteristic().info.uuid)

                measurement = ctx.other_characteristics.get(measurement_uuid)
                context = ctx.other_characteristics.get(context_uuid)

                if measurement is None:
                    raise ValueError("Measurement dependency must be present before Multi Dependency characteristic")

                if context is None:
                    raise ValueError("Context dependency must be present before Multi Dependency characteristic")

                result: dict[str, Any] = {
                    "measurement_ref": measurement_ref,
                    "context_ref": context_ref,
                    "measurement_value": measurement,
                    "context_value": context["context_value"],
                    "measurement_match": measurement == measurement_ref,
                    "context_match": context["context_value"] == context_ref,
                    "enriched": False,
                }

                enrichment = ctx.other_characteristics.get(optional_uuid)
                if enrichment is not None:
                    result["enriched"] = True
                    result["enriched_value"] = result["measurement_value"] * enrichment

                return result

            def _encode_value(self, data: dict[str, Any]) -> bytearray:
                measurement_ref = data.get("measurement_ref", 0)
                context_ref = data.get("context_ref", 0)
                return bytearray(
                    measurement_ref.to_bytes(2, byteorder="little", signed=False)
                    + context_ref.to_bytes(2, byteorder="little", signed=False)
                )

        # Register all characteristics
        translator.register_custom_characteristic_class(
            str(MeasurementCharacteristic().info.uuid), MeasurementCharacteristic, override=True
        )
        translator.register_custom_characteristic_class(
            str(ContextCharacteristic().info.uuid), ContextCharacteristic, override=True
        )
        translator.register_custom_characteristic_class(
            str(EnrichmentCharacteristic().info.uuid), EnrichmentCharacteristic, override=True
        )
        translator.register_custom_characteristic_class(
            str(DataCharacteristic().info.uuid), DataCharacteristic, override=True
        )
        translator.register_custom_characteristic_class(
            str(MultiDependencyCharacteristic().info.uuid), MultiDependencyCharacteristic, override=True
        )

        return translator

    def test_missing_required_dependency_fails_fast(self, translator: BluetoothSIGTranslator) -> None:
        """Test that missing required dependencies result in parse failure."""
        from bluetooth_sig.gatt.exceptions import MissingDependencyError

        # Try to parse context WITHOUT its required measurement
        char_data = {
            "C0111E11-0000-1000-8000-00805F9B34FB": (42).to_bytes(2, byteorder="little", signed=False),
        }

        with pytest.raises(MissingDependencyError) as exc_info:
            translator.parse_characteristics(char_data)

        assert "0EA50001-0000-1000-8000-00805F9B34FB" in str(exc_info.value)

    def test_optional_dependency_absent_still_succeeds(self, translator: BluetoothSIGTranslator) -> None:
        """Test that missing optional dependencies don't prevent parsing."""
        # Parse data WITHOUT its optional enrichment
        char_data = {
            "DA1A0001-0000-1000-8000-00805F9B34FB": (100).to_bytes(2, byteorder="little", signed=False),
        }

        results = translator.parse_characteristics(char_data)

        # Data should parse successfully without enrichment
        data_result = results["DA1A0001-0000-1000-8000-00805F9B34FB"]
        assert isinstance(data_result, dict)
        assert data_result["data_value"] == 100
        assert data_result["enriched"] is False

    def test_required_dependency_present_succeeds(self, translator: BluetoothSIGTranslator) -> None:
        """Test that required dependencies work when present."""
        char_data = {
            "0EA50001-0000-1000-8000-00805F9B34FB": (123).to_bytes(2, byteorder="little", signed=False),
            "C0111E11-0000-1000-8000-00805F9B34FB": (42).to_bytes(2, byteorder="little", signed=False),
        }

        results = translator.parse_characteristics(char_data)

        # Both should parse successfully
        measurement_result = results["0EA50001-0000-1000-8000-00805F9B34FB"]
        context_result = results["C0111E11-0000-1000-8000-00805F9B34FB"]

        assert measurement_result == 123

        assert isinstance(context_result, dict)
        assert context_result["context_value"] == 42
        assert context_result["has_measurement"] is True
        assert context_result["measurement_value"] == 123

    def test_optional_dependency_present_enriches(self, translator: BluetoothSIGTranslator) -> None:
        """Test that optional dependencies enrich parsing when available."""
        import struct

        char_data = {
            "E111C401-0000-1000-8000-00805F9B34FB": struct.pack("<f", 2.5),
            "DA1A0001-0000-1000-8000-00805F9B34FB": (100).to_bytes(2, byteorder="little", signed=False),
        }

        results = translator.parse_characteristics(char_data)

        # Both should parse successfully
        enrichment_result = results["E111C401-0000-1000-8000-00805F9B34FB"]
        data_result = results["DA1A0001-0000-1000-8000-00805F9B34FB"]

        assert enrichment_result == pytest.approx(2.5)

        assert isinstance(data_result, dict)
        assert data_result["data_value"] == 100
        assert data_result["enriched"] is True
        assert data_result["enriched_value"] == pytest.approx(250.0)

    def test_multi_dependency_missing_requirements_fails(self, translator: BluetoothSIGTranslator) -> None:
        """Multiple required dependencies must all be present."""
        from bluetooth_sig.gatt.exceptions import MissingDependencyError

        multi_uuid = "F0EADF11-0000-1000-8000-00805F9B34FB"
        # Provide raw value referencing measurement/context data that is not supplied
        multi_raw = (123).to_bytes(2, byteorder="little", signed=False) + (42).to_bytes(
            2, byteorder="little", signed=False
        )

        with pytest.raises(MissingDependencyError) as exc_info:
            translator.parse_characteristics({multi_uuid: multi_raw})

        assert "0EA50001-0000-1000-8000-00805F9B34FB" in str(exc_info.value)
        assert "C0111E11-0000-1000-8000-00805F9B34FB" in str(exc_info.value)

    def test_multi_dependency_with_required_only(self, translator: BluetoothSIGTranslator) -> None:
        """Multiple required dependencies allow parsing without optional enrichment."""
        measurement_uuid = "0EA50001-0000-1000-8000-00805F9B34FB"
        context_uuid = "C0111E11-0000-1000-8000-00805F9B34FB"
        multi_uuid = "F0EADF11-0000-1000-8000-00805F9B34FB"

        measurement_raw = (123).to_bytes(2, byteorder="little", signed=False)
        context_raw = (42).to_bytes(2, byteorder="little", signed=False)
        multi_raw = (123).to_bytes(2, byteorder="little", signed=False) + (42).to_bytes(
            2, byteorder="little", signed=False
        )

        results = translator.parse_characteristics(
            {
                measurement_uuid: measurement_raw,
                context_uuid: context_raw,
                multi_uuid: multi_raw,
            }
        )

        multi_result = results[multi_uuid]
        assert isinstance(multi_result, dict)
        assert multi_result["measurement_match"] is True
        assert multi_result["context_match"] is True
        assert multi_result["enriched"] is False

    def test_multi_dependency_with_optional_enrichment(self, translator: BluetoothSIGTranslator) -> None:
        """Optional dependency enriches result when provided."""
        import struct

        measurement_uuid = "0EA50001-0000-1000-8000-00805F9B34FB"
        context_uuid = "C0111E11-0000-1000-8000-00805F9B34FB"
        enrichment_uuid = "E111C401-0000-1000-8000-00805F9B34FB"
        multi_uuid = "F0EADF11-0000-1000-8000-00805F9B34FB"

        measurement_raw = (200).to_bytes(2, byteorder="little", signed=False)
        context_raw = (99).to_bytes(2, byteorder="little", signed=False)
        enrichment_raw = struct.pack("<f", 1.5)
        multi_raw = (200).to_bytes(2, byteorder="little", signed=False) + (99).to_bytes(
            2, byteorder="little", signed=False
        )

        results = translator.parse_characteristics(
            {
                enrichment_uuid: enrichment_raw,
                measurement_uuid: measurement_raw,
                context_uuid: context_raw,
                multi_uuid: multi_raw,
            }
        )

        multi_result = results[multi_uuid]
        assert isinstance(multi_result, dict)
        assert multi_result["measurement_match"] is True
        assert multi_result["context_match"] is True
        assert multi_result["enriched"] is True
        assert multi_result["enriched_value"] == pytest.approx(300.0)
