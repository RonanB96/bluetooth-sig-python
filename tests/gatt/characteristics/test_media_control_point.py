"""Tests for Media Control Point characteristic (0x2BA4)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.media_control_point import (
    MediaControlPointCharacteristic,
    MediaControlPointData,
    MediaControlPointOpCode,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMediaControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for Media Control Point characteristic."""

    @pytest.fixture
    def characteristic(self) -> MediaControlPointCharacteristic:
        return MediaControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BA4"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=MediaControlPointData(
                    op_code=MediaControlPointOpCode.PLAY,
                    parameter=None,
                ),
                description="Play (no parameter)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02]),
                expected_value=MediaControlPointData(
                    op_code=MediaControlPointOpCode.PAUSE,
                    parameter=None,
                ),
                description="Pause (no parameter)",
            ),
            CharacteristicTestData(
                # Move Relative with sint32 offset = -100 (0xFFFFFF9C little-endian)
                input_data=bytearray([0x06, 0x9C, 0xFF, 0xFF, 0xFF]),
                expected_value=MediaControlPointData(
                    op_code=MediaControlPointOpCode.MOVE_RELATIVE,
                    parameter=-100,
                ),
                description="Move Relative with negative offset",
            ),
            CharacteristicTestData(
                # Goto Track with sint32 number = 5 (0x00000005 little-endian)
                input_data=bytearray([0x24, 0x05, 0x00, 0x00, 0x00]),
                expected_value=MediaControlPointData(
                    op_code=MediaControlPointOpCode.GOTO_TRACK,
                    parameter=5,
                ),
                description="Goto Track with track number 5",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip for parameterised opcode."""
        char = MediaControlPointCharacteristic()
        original = MediaControlPointData(
            op_code=MediaControlPointOpCode.GOTO_GROUP,
            parameter=42,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_encode_round_trip_no_param(self) -> None:
        """Verify encode/decode round-trip for opcode without parameter."""
        char = MediaControlPointCharacteristic()
        original = MediaControlPointData(
            op_code=MediaControlPointOpCode.STOP,
            parameter=None,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
