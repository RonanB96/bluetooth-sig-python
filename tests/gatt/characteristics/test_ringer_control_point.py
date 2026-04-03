"""Tests for RingerControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.ringer_control_point import (
    RingerControlCommand,
    RingerControlPointCharacteristic,
    RingerControlPointData,
)


class TestRingerControlPointCharacteristic:
    """Test suite for RingerControlPointCharacteristic.

    This is a write-only characteristic — no _decode_value exists.
    Tests focus on _encode_value only.
    """

    @pytest.fixture
    def characteristic(self) -> RingerControlPointCharacteristic:
        return RingerControlPointCharacteristic()

    def test_uuid(self, characteristic: RingerControlPointCharacteristic) -> None:
        """Test that the UUID matches the expected value."""
        assert characteristic.uuid == "2A40"

    def test_encode_silent_mode(self, characteristic: RingerControlPointCharacteristic) -> None:
        """Test encoding SILENT_MODE command."""
        data = RingerControlPointData(command=RingerControlCommand.SILENT_MODE)
        encoded = characteristic._encode_value(data)
        assert encoded == bytearray([0x01])

    def test_encode_mute_once(self, characteristic: RingerControlPointCharacteristic) -> None:
        """Test encoding MUTE_ONCE command."""
        data = RingerControlPointData(command=RingerControlCommand.MUTE_ONCE)
        encoded = characteristic._encode_value(data)
        assert encoded == bytearray([0x03])

    def test_encode_cancel_silent_mode(self, characteristic: RingerControlPointCharacteristic) -> None:
        """Test encoding CANCEL_SILENT_MODE command."""
        data = RingerControlPointData(command=RingerControlCommand.CANCEL_SILENT_MODE)
        encoded = characteristic._encode_value(data)
        assert encoded == bytearray([0x02])

    def test_all_commands_encode_correctly(self, characteristic: RingerControlPointCharacteristic) -> None:
        """Test that all defined commands encode to their expected byte values."""
        expected = {
            RingerControlCommand.SILENT_MODE: bytearray([0x01]),
            RingerControlCommand.CANCEL_SILENT_MODE: bytearray([0x02]),
            RingerControlCommand.MUTE_ONCE: bytearray([0x03]),
        }
        for command, expected_bytes in expected.items():
            data = RingerControlPointData(command=command)
            assert characteristic._encode_value(data) == expected_bytes

    def test_invalid_command_value_rejected(self) -> None:
        """Test that reserved command values (0, 4-255) cannot be created."""
        with pytest.raises(ValueError):
            RingerControlCommand(0x00)

    def test_invalid_high_command_value_rejected(self) -> None:
        """Test that high reserved command values are rejected."""
        with pytest.raises(ValueError):
            RingerControlCommand(0x04)
