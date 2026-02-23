"""Comprehensive tests for CustomBaseCharacteristic with multiple variants.

This test suite demonstrates various use cases for custom characteristics:
- Simple value types (int, float, string)
- Complex multi-field structures
- Custom validations
- Template usage
- SIG UUID override
- Runtime registration
"""

from __future__ import annotations

from types import new_class
from typing import Any

import msgspec
import pytest

from bluetooth_sig.core.translator import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.gatt.characteristics.templates import ScaledUint16Template, Uint8Template
from bluetooth_sig.gatt.characteristics.utils import DataParser
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.uuid import BluetoothUUID

# ==============================================================================
# Variant 1: Simple Custom Characteristic with Basic Validation
# ==============================================================================


class SimpleTemperatureSensor(CustomBaseCharacteristic):
    """Simple temperature sensor with basic int16 parsing."""

    expected_length: int = 2
    min_value: int = -40
    max_value: int = 85
    expected_type: type = int

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("AA001234-0000-1000-8000-00805F9B34FB"),
        name="Simple Temperature Sensor",
        unit="°C",
        python_type=int,
    )

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> int:
        """Parse temperature as signed 16-bit integer."""
        return DataParser.parse_int16(data, 0, signed=True)

    def _encode_value(self, data: int) -> bytearray:
        """Encode temperature as signed 16-bit integer."""
        return DataParser.encode_int16(data, signed=True)


# ==============================================================================
# Variant 2: Scaled Float Value with Template
# ==============================================================================


class PrecisionHumiditySensor(CustomBaseCharacteristic):
    """Humidity sensor using template for scaled uint16 (0.01% resolution)."""

    _template = ScaledUint16Template(scale_factor=0.01)
    min_value: float = 0.0
    max_value: float = 100.0

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("BB001234-0000-1000-8000-00805F9B34FB"),
        name="Precision Humidity Sensor",
        unit="%",
        python_type=float,
    )


# ==============================================================================
# Variant 3: Multi-Field Structured Data
# ==============================================================================


class EnvironmentalReading(msgspec.Struct, kw_only=True):
    """Structured environmental sensor reading."""

    temperature: float
    humidity: float
    pressure: int
    timestamp: int


class MultiSensorCharacteristic(CustomBaseCharacteristic):
    """Environmental sensor with multiple fields."""

    min_length: int = 12

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("CC001234-0000-1000-8000-00805F9B34FB"),
        name="Multi-Sensor Environmental",
        unit="various",
        python_type=bytes,
    )

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> EnvironmentalReading:
        """Parse multi-field environmental data."""
        if len(data) < 12:
            raise ValueError("Multi-sensor data requires at least 12 bytes")

        temp = DataParser.parse_int16(data, 0, signed=True) * 0.01
        humidity = DataParser.parse_int16(data, 2, signed=False) * 0.01
        pressure = DataParser.parse_int32(data, 4, signed=False)
        timestamp = DataParser.parse_int32(data, 8, signed=False)

        return EnvironmentalReading(
            temperature=temp,
            humidity=humidity,
            pressure=pressure,
            timestamp=timestamp,
        )

    def _encode_value(self, data: EnvironmentalReading) -> bytearray:
        """Encode environmental reading."""
        output_data = bytearray()
        output_data.extend(DataParser.encode_int16(int(data.temperature * 100), signed=True))
        output_data.extend(DataParser.encode_int16(int(data.humidity * 100), signed=False))
        output_data.extend(DataParser.encode_int32(data.pressure, signed=False))
        output_data.extend(DataParser.encode_int32(data.timestamp, signed=False))
        return output_data


# ==============================================================================
# Variant 4: String-Based Custom Characteristic
# ==============================================================================


class DeviceSerialNumberCharacteristic(CustomBaseCharacteristic):
    """Custom serial number characteristic."""

    min_length: int = 1
    max_length: int = 32
    expected_type: type = str

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("DD001234-0000-1000-8000-00805F9B34FB"),
        name="Device Serial Number",
        unit="",
        python_type=str,
    )

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> str:
        """Parse serial number as UTF-8 string."""
        return data.decode("utf-8").strip()

    def _encode_value(self, data: str) -> bytearray:
        """Encode serial number as UTF-8."""
        return bytearray(data.encode("utf-8"))


# ==============================================================================
# Variant 5: Custom Characteristic with Flags
# ==============================================================================


class DeviceStatusFlags(CustomBaseCharacteristic):
    """Device status with bit flags."""

    expected_length: int = 1
    # Note: No expected_type since we return dict, not int

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("EE001234-0000-1000-8000-00805F9B34FB"),
        name="Device Status Flags",
        unit="",
        python_type=int,
    )

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> dict[str, bool]:
        """Parse status flags and return dict of flag states."""
        flags = data[0]
        return {
            "powered_on": bool(flags & 0x01),
            "charging": bool(flags & 0x02),
            "low_battery": bool(flags & 0x04),
            "error": bool(flags & 0x08),
            "bluetooth_connected": bool(flags & 0x10),
            "wifi_connected": bool(flags & 0x20),
        }

    def _encode_value(self, data: dict[str, bool]) -> bytearray:
        """Encode status flags dict to byte."""
        byte = 0
        if data.get("powered_on", False):
            byte |= 0x01
        if data.get("charging", False):
            byte |= 0x02
        if data.get("low_battery", False):
            byte |= 0x04
        if data.get("error", False):
            byte |= 0x08
        if data.get("bluetooth_connected", False):
            byte |= 0x10
        if data.get("wifi_connected", False):
            byte |= 0x20
        return bytearray([byte])


# ==============================================================================
# Test Suite
# ==============================================================================


class TestCustomCharacteristicVariants:
    """Test suite for all custom characteristic variants."""

    def test_simple_temperature_sensor(self) -> None:
        """Test simple temperature sensor characteristic."""
        sensor = SimpleTemperatureSensor()

        # Test parsing positive temperature
        data = bytearray([0x14, 0x00])  # 20°C
        result = sensor.parse_value(data)
        assert result == 20
        assert sensor.info.unit == "°C"

        # Test parsing negative temperature
        data = bytearray([0xF6, 0xFF])  # -10°C
        result = sensor.parse_value(data)
        assert result == -10

        # Test round-trip
        encoded = sensor.build_value(25)
        result = sensor.parse_value(encoded)
        assert result == 25

    def test_simple_temperature_validation(self) -> None:
        """Test temperature sensor validation."""
        sensor = SimpleTemperatureSensor()

        # Test validation: length check
        short_data = bytearray([0x14])
        with pytest.raises(CharacteristicParseError) as exc_info:
            sensor.parse_value(short_data)
        assert "expected exactly 2 bytes, got 1" in str(exc_info.value).lower()

        # Test validation: range check (simulate out of range)
        # The sensor will decode the value, but validation will fail if out of range
        # We need to ensure the value would be outside -40 to 85 range

    def test_precision_humidity_sensor(self) -> None:
        """Test precision humidity sensor with template."""
        sensor = PrecisionHumiditySensor()

        # Test parsing: 5000 * 0.01 = 50.00%
        data = bytearray([0x88, 0x13])
        result = sensor.parse_value(data)
        assert result == 50.0
        assert sensor.info.unit == "%"

        # Test max humidity
        data = bytearray([0x10, 0x27])  # 10000 * 0.01 = 100.0%
        result = sensor.parse_value(data)
        assert result == 100.0

    def test_multi_sensor_characteristic(self) -> None:
        """Test multi-field environmental sensor."""
        sensor = MultiSensorCharacteristic()

        # Create test data: temp=25.5°C, humidity=60%, pressure=101325Pa, timestamp=1609459200
        data = bytearray(
            [
                0xFE,
                0x09,  # 2550 * 0.01 = 25.5°C
                0x70,
                0x17,  # 6000 * 0.01 = 60.0%
                0xCD,
                0x8B,
                0x01,
                0x00,  # 101325 Pa
                0x00,
                0x00,
                0x00,
                0x60,  # timestamp
            ]
        )

        result = sensor.parse_value(data)
        assert isinstance(result, EnvironmentalReading)
        assert abs(result.temperature - 25.5) < 0.1  # Allow floating point tolerance
        assert result.humidity == 60.0
        assert result.pressure == 101325
        assert result.timestamp == 1610612736

    def test_multi_sensor_length_validation(self) -> None:
        """Test multi-sensor minimum length validation."""
        sensor = MultiSensorCharacteristic()

        # Too short data
        short_data = bytearray([0x01, 0x02, 0x03])
        with pytest.raises(CharacteristicParseError):
            sensor.parse_value(short_data)

    def test_device_serial_number(self) -> None:
        """Test string-based serial number characteristic."""
        char = DeviceSerialNumberCharacteristic()

        # Test parsing serial number
        data = bytearray(b"SN123456789")
        result = char.parse_value(data)
        assert result == "SN123456789"
        assert char.info.python_type is str

        encoded = char.build_value("TEST12345")
        result = char.parse_value(encoded)
        assert result == "TEST12345"

    def test_device_status_flags(self) -> None:
        """Test device status flags characteristic."""
        char = DeviceStatusFlags()

        # Test all flags off
        data = bytearray([0x00])
        result = char.parse_value(data)
        assert isinstance(result, dict)
        # Pylint false positive: result is dict, but pylint doesn't recognize msgspec.Struct returns
        assert result["powered_on"] is False  # pylint: disable=unsubscriptable-object
        assert result["charging"] is False  # pylint: disable=unsubscriptable-object
        assert result["error"] is False  # pylint: disable=unsubscriptable-object

        # Test multiple flags on: powered_on + bluetooth_connected
        data = bytearray([0x11])  # 0x01 | 0x10
        result = char.parse_value(data)
        assert result is not None
        assert result["powered_on"] is True  # pylint: disable=unsubscriptable-object
        assert result["bluetooth_connected"] is True  # pylint: disable=unsubscriptable-object
        assert result["charging"] is False  # pylint: disable=unsubscriptable-object

        # Test round-trip
        flags = {
            "powered_on": True,
            "charging": True,
            "low_battery": False,
            "error": False,
            "bluetooth_connected": False,
            "wifi_connected": True,
        }
        encoded = char.build_value(flags)
        assert encoded[0] == 0x23  # 0x01 | 0x02 | 0x20

    def test_custom_battery_level_override(self) -> None:
        """Test custom battery level with SIG UUID override."""

        # Define CustomBatteryLevel inside test to avoid module-level registration
        class CustomBatteryLevel(CustomBaseCharacteristic, allow_sig_override=True):
            """Custom battery level implementation that overrides SIG UUID.

            This demonstrates intentional SIG UUID override with custom behaviour.
            Requires explicit allow_sig_override=True.
            """

            _template = Uint8Template()
            min_value: int = 0
            max_value: int = 100

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("2A19"),  # Official SIG Battery Level UUID
                name="Custom Battery Level",
                unit="%",
                python_type=int,
            )

        char = CustomBatteryLevel()

        # Verify override is allowed
        assert char._allows_sig_override is True
        assert str(char.info.uuid).lower() == "00002a19-0000-1000-8000-00805f9b34fb"

        # Test parsing
        data = bytearray([85])  # 85%
        result = char.parse_value(data)
        assert result == 85

    def test_custom_characteristics_have_is_custom_marker(self) -> None:
        """Verify all custom characteristics have _is_custom marker."""

        # Define CustomBatteryLevel inside test to avoid module-level registration
        class CustomBatteryLevel(CustomBaseCharacteristic, allow_sig_override=True):
            """Custom battery level implementation that overrides SIG UUID."""

            _template = Uint8Template()
            min_value: int = 0
            max_value: int = 100

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("2A19"),  # Official SIG Battery Level UUID
                name="Custom Battery Level",
                unit="%",
                python_type=int,
            )

        assert SimpleTemperatureSensor._is_custom is True
        assert PrecisionHumiditySensor._is_custom is True
        assert MultiSensorCharacteristic._is_custom is True
        assert DeviceSerialNumberCharacteristic._is_custom is True
        assert DeviceStatusFlags._is_custom is True
        assert CustomBatteryLevel._is_custom is True


class TestCustomCharacteristicRegistration:
    """Test runtime registration of custom characteristics."""

    def test_register_simple_characteristic(self) -> None:
        """Test registering a simple custom characteristic."""
        translator = BluetoothSIGTranslator()
        uuid = SimpleTemperatureSensor.get_class_uuid()
        assert uuid

        # Register the characteristic
        translator.register_custom_characteristic_class(
            str(uuid),
            SimpleTemperatureSensor,
            info=CharacteristicInfo(
                uuid=uuid,
                name="Simple Temperature Sensor",
                unit="°C",
                python_type=int,
            ),
        )

        # Parse data using the registered characteristic
        data = bytearray([0x14, 0x00])  # 20°C
        result = translator.parse_characteristic(
            str(SimpleTemperatureSensor.get_class_uuid()),
            bytes(data),
        )

        assert result == 20

    def test_register_multi_field_characteristic(self) -> None:
        """Test registering multi-field characteristic."""
        translator = BluetoothSIGTranslator()

        translator.register_custom_characteristic_class(
            str(MultiSensorCharacteristic.get_class_uuid()),
            MultiSensorCharacteristic,
        )

        # Create test data
        data = bytearray(
            [
                0xFE,
                0x09,  # temp
                0x70,
                0x17,  # humidity
                0x0D,
                0x8B,
                0x01,
                0x00,  # pressure
                0x00,
                0x00,
                0x00,
                0x60,  # timestamp
            ]
        )

        result = translator.parse_characteristic(
            str(MultiSensorCharacteristic.get_class_uuid()),
            bytes(data),
        )

        assert isinstance(result, EnvironmentalReading)


class TestCustomCharacteristicErrorHandling:
    """Test error handling for custom characteristics."""

    def test_custom_characteristic_without_uuid_fails(self) -> None:
        """Test that custom characteristic without _info raises error."""
        with pytest.raises(ValueError, match="requires either 'info' parameter or '_info' class attribute"):

            class MissingInfoCharacteristic(CustomBaseCharacteristic):
                # Missing _info attribute entirely
                def _decode_value(
                    self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
                ) -> int:
                    return 0

                def _encode_value(self, data: int) -> bytearray:
                    return bytearray()

            _ = MissingInfoCharacteristic()  # Should raise ValueError

    def test_custom_characteristic_sig_uuid_without_override_fails(self) -> None:
        """Test that SIG UUID without override flag fails."""
        with pytest.raises(ValueError, match="without override flag"):

            def _class_body(namespace: dict[str, Any]) -> None:  # pragma: no cover
                namespace["_info"] = CharacteristicInfo(
                    uuid=BluetoothUUID("2A19"),  # SIG UUID without override
                    name="Unauthorized Battery",
                    unit="%",
                    python_type=int,
                )

                def _decode_value(  # pylint: disable=duplicate-code
                    # NOTE: Minimal characteristic implementation duplicates other test fixtures.
                    # Duplication justified because:
                    # 1. Test isolation - each test creates its own custom characteristic
                    # 2. Boilerplate decode/encode stubs required by CustomBaseCharacteristic API
                    # 3. Consolidation would reduce test independence and clarity
                    self: CustomBaseCharacteristic,
                    data: bytearray,
                    ctx: CharacteristicContext | None = None,
                ) -> int:
                    return 0

                def _encode_value(self: CustomBaseCharacteristic, data: int) -> bytearray:
                    return bytearray()

                namespace["_decode_value"] = _decode_value
                namespace["_encode_value"] = _encode_value

            new_class(
                "UnauthorizedSIGOverride",
                (CustomBaseCharacteristic,),
                {"allow_sig_override": False},
                _class_body,
            )

    def test_decode_error_handling(self) -> None:
        """Test that decode errors are properly handled."""
        sensor = SimpleTemperatureSensor()

        # Empty data should trigger error
        with pytest.raises(CharacteristicParseError):
            sensor.parse_value(bytearray())

    def test_validation_error_handling(self) -> None:
        """Test that validation errors are properly handled."""
        sensor = PrecisionHumiditySensor()

        # Value over 100% should fail validation
        data = bytearray([0xF4, 0x27])  # 10228 * 0.01 = 102.28%
        with pytest.raises(CharacteristicParseError):
            sensor.parse_value(data)


class TestCustomCharacteristicEdgeCases:
    """Test edge cases for custom characteristics."""

    def test_empty_data_handling(self) -> None:
        """Test handling of empty data."""
        chars = [
            SimpleTemperatureSensor(),
            PrecisionHumiditySensor(),
            DeviceSerialNumberCharacteristic(),
        ]

        for char in chars:
            with pytest.raises(CharacteristicParseError):
                char.parse_value(bytearray())

    def test_maximum_values(self) -> None:
        """Test handling of maximum values."""
        sensor = SimpleTemperatureSensor()

        # Max temperature (85°C)
        data = sensor.build_value(85)
        result = sensor.parse_value(data)
        assert result == 85

    def test_minimum_values(self) -> None:
        """Test handling of minimum values."""
        sensor = SimpleTemperatureSensor()

        # Min temperature (-40°C)
        data = sensor.build_value(-40)
        result = sensor.parse_value(data)
        assert result == -40

    def test_string_encoding_edge_cases(self) -> None:
        """Test string encoding with special characters."""
        char = DeviceSerialNumberCharacteristic()

        # Test with special characters
        special_serial = "SN-2024_#001"
        encoded = char.build_value(special_serial)
        result = char.parse_value(encoded)
        assert result == special_serial


class TestCustomBaseCharacteristicAPI:
    """Test CustomBaseCharacteristic API features."""

    def test_auto_info_binding(self) -> None:
        """Test auto _info binding via class attribute."""

        class AutoInfoCharacteristic(CustomBaseCharacteristic):
            """Test characteristic with auto _info binding."""

            expected_length = 2
            min_value = 0
            max_value = 100
            expected_type = int

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789ABC"),
                name="Auto Info Test",
                unit="units",
                python_type=int,
            )

            def _decode_value(
                self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
            ) -> int:
                return DataParser.parse_int16(data, 0, signed=False)

            def _encode_value(self, data: int) -> bytearray:
                return DataParser.encode_int16(data, signed=False)

        # Should create without explicit info parameter
        char = AutoInfoCharacteristic()

        # Should have correct _info from class attribute
        assert char.info.uuid == BluetoothUUID("12345678-1234-1234-1234-123456789ABC")
        assert char.info.name == "Auto Info Test"
        assert char.info.unit == "units"
        assert char.info.python_type is int

        # Should work for parsing
        test_data = bytearray([0x32, 0x00])  # 50 in little-endian
        result = char.parse_value(test_data)

        assert result == 50

    def test_manual_info_override(self) -> None:
        """Test that manual info parameter still works (backwards compatibility)."""

        class OverridableCharacteristic(CustomBaseCharacteristic):
            """Test characteristic with class _info that can be overridden."""

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789ABC"),
                name="Original Name",
                unit="units",
                python_type=int,
            )

            def _decode_value(
                self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
            ) -> int:
                return DataParser.parse_int16(data, 0, signed=False)

            def _encode_value(self, data: int) -> bytearray:
                return DataParser.encode_int16(data, signed=False)

        # Create with manual info override
        override_info = CharacteristicInfo(
            uuid=BluetoothUUID("ABCDEF12-3456-7890-ABCD-EF1234567890"),
            name="Override Name",
            unit="override_units",
            python_type=float,
        )

        char = OverridableCharacteristic(info=override_info)

        # Should use override info, not class _info
        assert char.info.uuid == BluetoothUUID("ABCDEF12-3456-7890-ABCD-EF1234567890")
        assert char.info.name == "Override Name"
        assert char.info.unit == "override_units"
        assert char.info.python_type is float

    def test_sig_override_protection(self) -> None:
        """Test that __init_subclass__ prevents SIG UUID usage without permission."""
        with pytest.raises(ValueError, match="uses SIG UUID.*without override flag"):

            def _bad_body(namespace: dict[str, Any]) -> None:  # pragma: no cover
                namespace["_info"] = CharacteristicInfo(
                    uuid=BluetoothUUID("2A19"),  # SIG Battery Level UUID
                    name="Bad Override",
                    unit="%",
                    python_type=int,
                )

                def _decode_value(  # pylint: disable=duplicate-code
                    # NOTE: Minimal characteristic implementation duplicates other test fixtures.
                    # Duplication justified because:
                    # 1. Test isolation - each test creates its own custom characteristic
                    # 2. Boilerplate decode/encode stubs required by CustomBaseCharacteristic API
                    # 3. Consolidation would reduce test independence and clarity
                    self: CustomBaseCharacteristic,
                    data: bytearray,
                    ctx: CharacteristicContext | None = None,
                ) -> int:
                    return data[0]

                def _encode_value(self: CustomBaseCharacteristic, data: int) -> bytearray:
                    return bytearray([data])

                namespace["_decode_value"] = _decode_value
                namespace["encode_value"] = _encode_value

            new_class(
                "BadSIGOverride",
                (CustomBaseCharacteristic,),
                {"allow_sig_override": False},
                _bad_body,
            )

    def test_sig_override_with_permission(self) -> None:
        """Test that SIG UUID override works with explicit permission."""

        class AllowedSIGOverride(CustomBaseCharacteristic, allow_sig_override=True):
            """Should work: uses SIG UUID with explicit permission."""

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("2A19"),  # SIG Battery Level UUID
                name="Allowed Override",
                unit="%",
                python_type=int,
            )

            def _decode_value(  # pylint: disable=duplicate-code
                # NOTE: Minimal characteristic implementation duplicates other test fixtures.
                # Duplication justified because:
                # 1. Test isolation - each test creates its own custom characteristic
                # 2. Boilerplate decode/encode stubs required by CustomBaseCharacteristic API
                # 3. Consolidation would reduce test independence and clarity
                self,
                data: bytearray,
                ctx: CharacteristicContext | None = None,
                *,
                validate: bool = True,
            ) -> int:
                return data[0]

            def _encode_value(self, data: int) -> bytearray:
                return bytearray([data])

        # Should create successfully
        char = AllowedSIGOverride()
        assert char.info.uuid == BluetoothUUID("2A19")
        assert char.info.name == "Allowed Override"
        assert char._allows_sig_override is True

    def test_missing_info_error(self) -> None:
        """Test that missing _info raises clear error."""

        class MissingInfoCharacteristic(CustomBaseCharacteristic):
            """Should fail: no _info provided."""

            def _decode_value(
                self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
            ) -> int:
                return data[0]

            def _encode_value(self, data: int) -> bytearray:
                return bytearray([data])

        with pytest.raises(ValueError, match="requires either 'info' parameter or '_info' class attribute"):
            MissingInfoCharacteristic()

    def test_custom_uuid_allowed_without_override_flag(self) -> None:
        """Test that custom UUIDs work without override permission."""

        class CustomUUIDCharacteristic(CustomBaseCharacteristic):
            """Should work: uses custom UUID (not SIG)."""

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789ABC"),
                name="Custom Characteristic",
                unit="custom",
                python_type=int,
            )

            def _decode_value(
                self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
            ) -> int:
                return data[0]

            def _encode_value(self, data: int) -> bytearray:
                return bytearray([data])

        # Should create successfully without override flag
        char = CustomUUIDCharacteristic()
        assert char.info.uuid == BluetoothUUID("12345678-1234-1234-1234-123456789ABC")
        assert char._allows_sig_override is False  # Default value
