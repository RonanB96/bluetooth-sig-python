"""Tests for Boot Keyboard Output Report characteristic (0x2A32)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import BootKeyboardOutputReportCharacteristic
from bluetooth_sig.gatt.characteristics.boot_keyboard_output_report import KeyboardLEDs
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBootKeyboardOutputReportCharacteristic(CommonCharacteristicTests):
    """Test suite for Boot Keyboard Output Report characteristic."""

    @pytest.fixture
    def characteristic(self) -> BootKeyboardOutputReportCharacteristic:
        """Return a Boot Keyboard Output Report characteristic instance."""
        return BootKeyboardOutputReportCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Boot Keyboard Output Report characteristic."""
        return "2A32"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for boot keyboard output report."""
        return [
            CharacteristicTestData(input_data=bytearray([0]), expected_value=KeyboardLEDs(0), description="No LEDs on"),
            CharacteristicTestData(
                input_data=bytearray([1]), expected_value=KeyboardLEDs.NUM_LOCK, description="Num Lock on"
            ),
            CharacteristicTestData(
                input_data=bytearray([2]), expected_value=KeyboardLEDs.CAPS_LOCK, description="Caps Lock on"
            ),
            CharacteristicTestData(
                input_data=bytearray([4]),
                expected_value=KeyboardLEDs.SCROLL_LOCK,
                description="Scroll Lock on",
            ),
        ]

    def test_no_leds(self) -> None:
        """Test output report with no LEDs on."""
        char = BootKeyboardOutputReportCharacteristic()
        result = char.parse_value(bytearray([0]))
        assert result == KeyboardLEDs(0)

    def test_num_lock_on(self) -> None:
        """Test Num Lock LED on."""
        char = BootKeyboardOutputReportCharacteristic()
        result = char.parse_value(bytearray([1]))
        assert result == KeyboardLEDs.NUM_LOCK

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = BootKeyboardOutputReportCharacteristic()
        for value in [
            KeyboardLEDs(0),
            KeyboardLEDs.NUM_LOCK,
            KeyboardLEDs.CAPS_LOCK,
            KeyboardLEDs.SCROLL_LOCK,
            KeyboardLEDs.NUM_LOCK | KeyboardLEDs.CAPS_LOCK | KeyboardLEDs.SCROLL_LOCK,
        ]:
            encoded = char.build_value(value)
            decoded = char.parse_value(encoded)
            assert decoded == value
