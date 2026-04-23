"""Tests for vendor/proprietary parser registration examples.

Validates that the example vendor parsers in ``examples/vendor_parsers/``
produce correct output when run against simulated payloads via the
``BluetoothSIGTranslator``.
"""

from __future__ import annotations

import struct

import pytest

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from examples.vendor_parsers.register_parsers import (
    GOVEE_THERMO_UUID,
    NUS_BUTTON_UUID,
    NUS_LED_UUID,
    GoveeThermometerCharacteristic,
    GoveeThermometerReading,
    NordicButtonCharacteristic,
    NordicLEDCharacteristic,
    register_all,
)


@pytest.fixture(autouse=True)
def _registered_translator() -> BluetoothSIGTranslator:
    """Ensure all vendor parsers are registered before each test."""
    return register_all()


# ---------------------------------------------------------------------------
# Nordic LED characteristic
# ---------------------------------------------------------------------------


class TestNordicLEDCharacteristic:
    """Tests for the Nordic LBS LED state characteristic."""

    def test_parse_led_on(self) -> None:
        """LED state byte 0x01 decodes to 1 (on)."""
        char = NordicLEDCharacteristic()
        result = char.parse_value(bytearray([0x01]))
        assert result == 1

    def test_parse_led_off(self) -> None:
        """LED state byte 0x00 decodes to 0 (off)."""
        char = NordicLEDCharacteristic()
        result = char.parse_value(bytearray([0x00]))
        assert result == 0

    def test_encode_led_on(self) -> None:
        """Encoding 1 produces a single byte 0x01."""
        char = NordicLEDCharacteristic()
        encoded = char.build_value(1)
        assert encoded == bytearray([0x01])

    def test_encode_led_off(self) -> None:
        """Encoding 0 produces a single byte 0x00."""
        char = NordicLEDCharacteristic()
        encoded = char.build_value(0)
        assert encoded == bytearray([0x00])

    def test_round_trip_on(self) -> None:
        """Parse(encode(1)) == 1."""
        char = NordicLEDCharacteristic()
        assert char.parse_value(char.build_value(1)) == 1

    def test_round_trip_off(self) -> None:
        """Parse(encode(0)) == 0."""
        char = NordicLEDCharacteristic()
        assert char.parse_value(char.build_value(0)) == 0

    def test_empty_payload_raises(self) -> None:
        """Empty payload raises CharacteristicParseError."""
        char = NordicLEDCharacteristic()
        with pytest.raises(CharacteristicParseError):
            char.parse_value(bytearray([]))

    def test_translator_dispatches_by_uuid(self) -> None:
        """Translator correctly dispatches LED UUID to NordicLEDCharacteristic."""
        translator = BluetoothSIGTranslator.get_instance()
        result = translator.parse_characteristic(NUS_LED_UUID, bytearray([0x01]))
        assert result == 1


# ---------------------------------------------------------------------------
# Nordic Button characteristic
# ---------------------------------------------------------------------------


class TestNordicButtonCharacteristic:
    """Tests for the Nordic LBS button state characteristic."""

    def test_parse_button_pressed(self) -> None:
        """Button byte 0x01 decodes to 1 (pressed)."""
        char = NordicButtonCharacteristic()
        result = char.parse_value(bytearray([0x01]))
        assert result == 1

    def test_parse_button_released(self) -> None:
        """Button byte 0x00 decodes to 0 (released)."""
        char = NordicButtonCharacteristic()
        result = char.parse_value(bytearray([0x00]))
        assert result == 0

    def test_empty_payload_raises(self) -> None:
        """Empty payload raises CharacteristicParseError."""
        char = NordicButtonCharacteristic()
        with pytest.raises(CharacteristicParseError):
            char.parse_value(bytearray([]))

    def test_translator_dispatches_by_uuid(self) -> None:
        """Translator correctly dispatches button UUID to NordicButtonCharacteristic."""
        translator = BluetoothSIGTranslator.get_instance()
        result = translator.parse_characteristic(NUS_BUTTON_UUID, bytearray([0x00]))
        assert result == 0


# ---------------------------------------------------------------------------
# Govee thermometer characteristic
# ---------------------------------------------------------------------------


class TestGoveeThermometerCharacteristic:
    """Tests for the Govee-style temperature + humidity characteristic."""

    def test_parse_typical_reading(self) -> None:
        """Parse a typical 22.50 °C / 65.10 % payload."""
        char = GoveeThermometerCharacteristic()
        payload = bytearray(struct.pack("<hH", 2250, 6510))
        result = char.parse_value(payload)
        assert isinstance(result, GoveeThermometerReading)
        assert result.temperature == pytest.approx(22.5, abs=0.01)
        assert result.humidity == pytest.approx(65.1, abs=0.01)

    def test_parse_freezing_temperature(self) -> None:
        """Parse a sub-zero temperature: -5.00 °C / 30.00 %."""
        char = GoveeThermometerCharacteristic()
        payload = bytearray(struct.pack("<hH", -500, 3000))
        result = char.parse_value(payload)
        assert result.temperature == pytest.approx(-5.0, abs=0.01)
        assert result.humidity == pytest.approx(30.0, abs=0.01)

    def test_parse_max_values(self) -> None:
        """Parse edge case: 0 °C / 100.00 % humidity."""
        char = GoveeThermometerCharacteristic()
        payload = bytearray(struct.pack("<hH", 0, 10000))
        result = char.parse_value(payload)
        assert result.temperature == pytest.approx(0.0, abs=0.01)
        assert result.humidity == pytest.approx(100.0, abs=0.01)

    def test_encode_and_round_trip(self) -> None:
        """Encode then parse produces the original values."""
        char = GoveeThermometerCharacteristic()
        original = GoveeThermometerReading(temperature=18.75, humidity=52.50)
        encoded = char.build_value(original)
        assert len(encoded) == 4
        restored = char.parse_value(encoded)
        assert restored.temperature == pytest.approx(18.75, abs=0.01)
        assert restored.humidity == pytest.approx(52.50, abs=0.01)

    def test_too_short_payload_raises(self) -> None:
        """Payload shorter than 4 bytes raises CharacteristicParseError."""
        char = GoveeThermometerCharacteristic()
        with pytest.raises(CharacteristicParseError):
            char.parse_value(bytearray([0xCA, 0x08]))

    def test_empty_payload_raises(self) -> None:
        """Empty payload raises CharacteristicParseError."""
        char = GoveeThermometerCharacteristic()
        with pytest.raises(CharacteristicParseError):
            char.parse_value(bytearray([]))

    def test_translator_dispatches_by_uuid(self) -> None:
        """Translator correctly dispatches Govee UUID to GoveeThermometerCharacteristic."""
        translator = BluetoothSIGTranslator.get_instance()
        payload = bytearray(struct.pack("<hH", 2250, 6510))
        result = translator.parse_characteristic(GOVEE_THERMO_UUID, payload)
        assert isinstance(result, GoveeThermometerReading)
        assert result.temperature == pytest.approx(22.5, abs=0.01)
        assert result.humidity == pytest.approx(65.1, abs=0.01)

    def test_translator_unknown_uuid_raises(self) -> None:
        """Translator raises for completely unknown UUID after registration."""
        translator = BluetoothSIGTranslator.get_instance()
        with pytest.raises(CharacteristicParseError):
            translator.parse_characteristic(
                "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF",
                bytearray([0x01]),
            )
