"""Tests for Pushbutton Status 8 characteristic (0x2C21)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.pushbutton_status_8 import (
    ButtonStatus,
    PushbuttonStatus8Characteristic,
    PushbuttonStatus8Data,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestPushbuttonStatus8Characteristic(CommonCharacteristicTests):
    """Test Pushbutton Status 8 characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide Pushbutton Status 8 characteristic for testing."""
        return PushbuttonStatus8Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Pushbutton Status 8."""
        return "2C21"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid pushbutton status test data covering various combinations."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=PushbuttonStatus8Data(
                    button_0=ButtonStatus.NOT_ACTUATED,
                    button_1=ButtonStatus.NOT_ACTUATED,
                    button_2=ButtonStatus.NOT_ACTUATED,
                    button_3=ButtonStatus.NOT_ACTUATED,
                ),
                description="All buttons not actuated",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=PushbuttonStatus8Data(
                    button_0=ButtonStatus.PRESSED,
                    button_1=ButtonStatus.NOT_ACTUATED,
                    button_2=ButtonStatus.NOT_ACTUATED,
                    button_3=ButtonStatus.NOT_ACTUATED,
                ),
                description="Button 0 pressed",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x04]),
                expected_value=PushbuttonStatus8Data(
                    button_0=ButtonStatus.NOT_ACTUATED,
                    button_1=ButtonStatus.PRESSED,
                    button_2=ButtonStatus.NOT_ACTUATED,
                    button_3=ButtonStatus.NOT_ACTUATED,
                ),
                description="Button 1 pressed",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x10]),
                expected_value=PushbuttonStatus8Data(
                    button_0=ButtonStatus.NOT_ACTUATED,
                    button_1=ButtonStatus.NOT_ACTUATED,
                    button_2=ButtonStatus.PRESSED,
                    button_3=ButtonStatus.NOT_ACTUATED,
                ),
                description="Button 2 pressed",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x40]),
                expected_value=PushbuttonStatus8Data(
                    button_0=ButtonStatus.NOT_ACTUATED,
                    button_1=ButtonStatus.NOT_ACTUATED,
                    button_2=ButtonStatus.NOT_ACTUATED,
                    button_3=ButtonStatus.PRESSED,
                ),
                description="Button 3 pressed",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x55]),
                expected_value=PushbuttonStatus8Data(
                    button_0=ButtonStatus.PRESSED,
                    button_1=ButtonStatus.PRESSED,
                    button_2=ButtonStatus.PRESSED,
                    button_3=ButtonStatus.PRESSED,
                ),
                description="All buttons pressed",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xAA]),
                expected_value=PushbuttonStatus8Data(
                    button_0=ButtonStatus.RELEASED,
                    button_1=ButtonStatus.RELEASED,
                    button_2=ButtonStatus.RELEASED,
                    button_3=ButtonStatus.RELEASED,
                ),
                description="All buttons released",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x09]),
                expected_value=PushbuttonStatus8Data(
                    button_0=ButtonStatus.PRESSED,
                    button_1=ButtonStatus.RELEASED,
                    button_2=ButtonStatus.NOT_ACTUATED,
                    button_3=ButtonStatus.NOT_ACTUATED,
                ),
                description="Button 0 pressed, button 1 released",
            ),
        ]

    # === Pushbutton-Specific Tests ===

    def test_individual_button_isolation(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test that each 2-bit field is extracted independently."""
        # Button 0 at bits [1:0]
        result = characteristic.parse_value(bytearray([0x02]))
        assert result.button_0 == ButtonStatus.RELEASED
        assert result.button_1 == ButtonStatus.NOT_ACTUATED

        # Button 1 at bits [3:2]
        result = characteristic.parse_value(bytearray([0x08]))
        assert result.button_1 == ButtonStatus.RELEASED
        assert result.button_0 == ButtonStatus.NOT_ACTUATED

        # Button 2 at bits [5:4]
        result = characteristic.parse_value(bytearray([0x20]))
        assert result.button_2 == ButtonStatus.RELEASED
        assert result.button_3 == ButtonStatus.NOT_ACTUATED

        # Button 3 at bits [7:6]
        result = characteristic.parse_value(bytearray([0x80]))
        assert result.button_3 == ButtonStatus.RELEASED
        assert result.button_2 == ButtonStatus.NOT_ACTUATED

    def test_encoding(self, characteristic: PushbuttonStatus8Characteristic) -> None:
        """Test encoding PushbuttonStatus8Data to bytes."""
        # All not actuated
        data = PushbuttonStatus8Data(
            button_0=ButtonStatus.NOT_ACTUATED,
            button_1=ButtonStatus.NOT_ACTUATED,
            button_2=ButtonStatus.NOT_ACTUATED,
            button_3=ButtonStatus.NOT_ACTUATED,
        )
        assert characteristic.build_value(data) == bytearray([0x00])

        # All pressed
        data = PushbuttonStatus8Data(
            button_0=ButtonStatus.PRESSED,
            button_1=ButtonStatus.PRESSED,
            button_2=ButtonStatus.PRESSED,
            button_3=ButtonStatus.PRESSED,
        )
        assert characteristic.build_value(data) == bytearray([0x55])

        # Mixed
        data = PushbuttonStatus8Data(
            button_0=ButtonStatus.RELEASED,
            button_1=ButtonStatus.PRESSED,
            button_2=ButtonStatus.NOT_ACTUATED,
            button_3=ButtonStatus.RELEASED,
        )
        # 0b10_00_01_10 = 0x86
        assert characteristic.build_value(data) == bytearray([0x86])

    def test_round_trip(self, characteristic: PushbuttonStatus8Characteristic) -> None:  # type: ignore[override]
        """Test round-trip encoding/decoding preserves values."""
        test_bytes = [0x00, 0x01, 0x55, 0xAA, 0x09, 0x86, 0xFF]

        for raw in test_bytes:
            decoded = characteristic.parse_value(bytearray([raw]))
            encoded = characteristic.build_value(decoded)
            assert encoded == bytearray([raw]), f"Round-trip failed for 0x{raw:02X}"

    def test_characteristic_metadata(self, characteristic: PushbuttonStatus8Characteristic) -> None:
        """Test characteristic metadata."""
        assert characteristic.name == "Pushbutton Status 8"
        assert characteristic.uuid == "2C21"
