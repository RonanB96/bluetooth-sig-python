"""Tests for Boot Keyboard Input Report characteristic (0x2A22)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import BootKeyboardInputReportCharacteristic, BootKeyboardInputReportData
from bluetooth_sig.gatt.characteristics.boot_keyboard_input_report import KeyboardModifiers
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBootKeyboardInputReportCharacteristic(CommonCharacteristicTests):
    """Test suite for Boot Keyboard Input Report characteristic."""

    @pytest.fixture
    def characteristic(self) -> BootKeyboardInputReportCharacteristic:
        """Return a Boot Keyboard Input Report characteristic instance."""
        return BootKeyboardInputReportCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Boot Keyboard Input Report characteristic."""
        return "2A22"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for boot keyboard input report."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0, 0, 0, 0, 0, 0, 0, 0]),
                expected_value=BootKeyboardInputReportData(
                    modifiers=KeyboardModifiers(0), reserved=0, keycodes=(0, 0, 0, 0, 0, 0)
                ),
                description="No keys pressed",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0, 4, 0, 0, 0, 0, 0]),
                expected_value=BootKeyboardInputReportData(
                    modifiers=KeyboardModifiers.LEFT_SHIFT, reserved=0, keycodes=(4, 0, 0, 0, 0, 0)
                ),
                description="Left Shift + 'a' key",
            ),
        ]

    def test_no_keys_pressed(self) -> None:
        """Test report with no keys pressed."""
        char = BootKeyboardInputReportCharacteristic()
        result = char.decode_value(bytearray([0, 0, 0, 0, 0, 0, 0, 0]))
        assert result.modifiers == KeyboardModifiers(0)
        assert result.reserved == 0
        assert result.keycodes == (0, 0, 0, 0, 0, 0)

    def test_single_key_with_modifier(self) -> None:
        """Test single key with modifier."""
        char = BootKeyboardInputReportCharacteristic()
        result = char.decode_value(bytearray([0x02, 0, 4, 0, 0, 0, 0, 0]))
        assert result.modifiers == KeyboardModifiers.LEFT_SHIFT
        assert result.keycodes[0] == 4  # 'a' key

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve data."""
        char = BootKeyboardInputReportCharacteristic()
        original = BootKeyboardInputReportData(
            modifiers=KeyboardModifiers.LEFT_SHIFT, reserved=0, keycodes=(4, 5, 6, 0, 0, 0)
        )
        encoded = char.encode_value(original)
        decoded = char.decode_value(encoded)
        assert decoded == original
