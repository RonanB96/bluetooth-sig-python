"""Tests for Time Update Control Point characteristic (0x2A16)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.time_update_control_point import (
    TimeUpdateControlPointCharacteristic,
    TimeUpdateControlPointCommand,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTimeUpdateControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for Time Update Control Point characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Adds time update control point-specific validation and edge cases.
    """

    @pytest.fixture
    def characteristic(self) -> TimeUpdateControlPointCharacteristic:
        """Return a Time Update Control Point characteristic instance."""
        return TimeUpdateControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Time Update Control Point characteristic."""
        return "2A16"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for time update control point."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=TimeUpdateControlPointCommand.GET_REFERENCE_UPDATE,
                description="Get Reference Time Update command",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02]),
                expected_value=TimeUpdateControlPointCommand.CANCEL_REFERENCE_UPDATE,
                description="Cancel Reference Time Update command",
            ),
        ]

    def test_get_reference_update_command(self) -> None:
        """Test GET_REFERENCE_UPDATE command encoding/decoding."""
        char = TimeUpdateControlPointCharacteristic()
        command = TimeUpdateControlPointCommand.GET_REFERENCE_UPDATE

        # Test encoding
        encoded = char.build_value(command)
        assert encoded == bytearray([0x01])

        # Test decoding
        decoded = char.parse_value(encoded)
        assert decoded is not None
        assert decoded == command

    def test_cancel_reference_update_command(self) -> None:
        """Test CANCEL_REFERENCE_UPDATE command encoding/decoding."""
        char = TimeUpdateControlPointCharacteristic()
        command = TimeUpdateControlPointCommand.CANCEL_REFERENCE_UPDATE

        # Test encoding
        encoded = char.build_value(command)
        assert encoded == bytearray([0x02])

        # Test decoding
        decoded = char.parse_value(encoded)
        assert decoded is not None
        assert decoded == command

    def test_invalid_command_raises_error(self) -> None:
        """Test that invalid command values result in parse failure."""
        char = TimeUpdateControlPointCharacteristic()

        # Test invalid data during parsing - raises CharacteristicParseError
        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(bytearray([0xFF]))
        assert "invalid" in str(exc_info.value).lower()

    def test_command_enum_values(self) -> None:
        """Test that command enum has expected values."""
        assert TimeUpdateControlPointCommand.GET_REFERENCE_UPDATE.value == 0x01
        assert TimeUpdateControlPointCommand.CANCEL_REFERENCE_UPDATE.value == 0x02
