"""Tests for Boot Mouse Input Report characteristic (0x2A33)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import BootMouseInputReportCharacteristic, BootMouseInputReportData
from bluetooth_sig.gatt.characteristics.boot_mouse_input_report import MouseButtons
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBootMouseInputReportCharacteristic(CommonCharacteristicTests):
    """Test suite for Boot Mouse Input Report characteristic."""

    @pytest.fixture
    def characteristic(self) -> BootMouseInputReportCharacteristic:
        """Return a Boot Mouse Input Report characteristic instance."""
        return BootMouseInputReportCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Boot Mouse Input Report characteristic."""
        return "2A33"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for boot mouse input report."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0, 0, 0]),
                expected_value=BootMouseInputReportData(buttons=MouseButtons(0), x_displacement=0, y_displacement=0),
                description="No movement, no buttons",
            ),
            CharacteristicTestData(
                input_data=bytearray([1, 10, 20]),
                expected_value=BootMouseInputReportData(
                    buttons=MouseButtons.LEFT, x_displacement=10, y_displacement=20
                ),
                description="Left button + movement",
            ),
        ]

    def test_no_input(self) -> None:
        """Test report with no mouse input."""
        char = BootMouseInputReportCharacteristic()
        result = char.decode_value(bytearray([0, 0, 0]))
        assert result.buttons == 0
        assert result.x_displacement == 0
        assert result.y_displacement == 0

    def test_left_button_with_movement(self) -> None:
        """Test left button pressed with mouse movement."""
        char = BootMouseInputReportCharacteristic()
        result = char.decode_value(bytearray([1, 10, 20]))
        assert result.buttons == 1
        assert result.x_displacement == 10
        assert result.y_displacement == 20

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve data."""
        char = BootMouseInputReportCharacteristic()
        original = BootMouseInputReportData(
            buttons=MouseButtons.LEFT | MouseButtons.RIGHT, x_displacement=-5, y_displacement=15
        )
        encoded = char.encode_value(original)
        decoded = char.decode_value(encoded)
        assert decoded == original
