"""Tests for DigitalCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.digital import DigitalCharacteristic, DigitalSignalState
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDigitalCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> DigitalCharacteristic:
        return DigitalCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A56"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            # Single byte: 0x00 = 0b0000_0000 → all INACTIVE
            CharacteristicTestData(
                bytearray([0x00]),
                (
                    DigitalSignalState.INACTIVE,
                    DigitalSignalState.INACTIVE,
                    DigitalSignalState.INACTIVE,
                    DigitalSignalState.INACTIVE,
                ),
                "Single byte all inactive (0x00)",
            ),
            # Single byte: 0x05 = 0b0000_0101 → ACTIVE, ACTIVE, INACTIVE, INACTIVE
            CharacteristicTestData(
                bytearray([0x05]),
                (
                    DigitalSignalState.ACTIVE,
                    DigitalSignalState.ACTIVE,
                    DigitalSignalState.INACTIVE,
                    DigitalSignalState.INACTIVE,
                ),
                "Single byte mixed states (0x05 = 0b0000_0101)",
            ),
            # Single byte: 0xFF = 0b1111_1111 → all UNKNOWN
            CharacteristicTestData(
                bytearray([0xFF]),
                (
                    DigitalSignalState.UNKNOWN,
                    DigitalSignalState.UNKNOWN,
                    DigitalSignalState.UNKNOWN,
                    DigitalSignalState.UNKNOWN,
                ),
                "Single byte all unknown (0xFF)",
            ),
            # Two bytes: 0x1B, 0xE4
            # 0x1B = 0b0001_1011 → UNKNOWN, TRISTATE, ACTIVE, INACTIVE
            # 0xE4 = 0b1110_0100 → INACTIVE, ACTIVE, TRISTATE, UNKNOWN
            CharacteristicTestData(
                bytearray([0x1B, 0xE4]),
                (
                    DigitalSignalState.UNKNOWN,
                    DigitalSignalState.TRISTATE,
                    DigitalSignalState.ACTIVE,
                    DigitalSignalState.INACTIVE,
                    DigitalSignalState.INACTIVE,
                    DigitalSignalState.ACTIVE,
                    DigitalSignalState.TRISTATE,
                    DigitalSignalState.UNKNOWN,
                ),
                "Two bytes mixed states (0x1B, 0xE4)",
            ),
        ]

    def test_non_aligned_encode_pads_to_byte_boundary(self, characteristic: DigitalCharacteristic) -> None:
        """Test that non-byte-aligned signal encoding pads to byte boundaries.

        This verifies AIO spec compliance: data must be byte-aligned, so 3 signals
        result in 1 byte (with bits [7:4] = 0 for padding).
        """
        # 3 signals: ACTIVE, ACTIVE, ACTIVE
        # Each ACTIVE signal is 0b01 (integer 1).
        # Encoding places signals at bit positions 0-1, 2-3, 4-5, 6-7
        # Signal 0 (ACTIVE=1) at bits [1:0]: 1 << 0 = 1
        # Signal 1 (ACTIVE=1) at bits [3:2]: 1 << 2 = 4
        # Signal 2 (ACTIVE=1) at bits [5:4]: 1 << 4 = 16
        # Result: 1 | 4 | 16 = 21 = 0x15
        three_signals = (
            DigitalSignalState.ACTIVE,
            DigitalSignalState.ACTIVE,
            DigitalSignalState.ACTIVE,
        )
        encoded = characteristic.build_value(three_signals)

        # Verify encoding is 1 byte with value 0x15
        assert len(encoded) == 1
        assert encoded[0] == 0x15

        # When decoded without context (no Number of Digitals descriptor), all 4 signals are extracted
        decoded = characteristic.parse_value(encoded)
        expected_padded = (
            DigitalSignalState.ACTIVE,
            DigitalSignalState.ACTIVE,
            DigitalSignalState.ACTIVE,
            DigitalSignalState.INACTIVE,
        )
        assert decoded == expected_padded

    def test_specific_bit_patterns(self, characteristic: DigitalCharacteristic) -> None:
        """Test specific bit patterns to verify little-endian bit extraction."""
        # 0x05 = 0b0000_0101: bits[1:0]=0b01, bits[3:2]=0b01, bits[5:4]=0b00, bits[7:6]=0b00
        result = characteristic.parse_value(bytearray([0x05]))
        expected = (
            DigitalSignalState.ACTIVE,
            DigitalSignalState.ACTIVE,
            DigitalSignalState.INACTIVE,
            DigitalSignalState.INACTIVE,
        )
        assert result == expected

        # 0xA0 = 0b1010_0000: bits[1:0]=0b00, bits[3:2]=0b00, bits[5:4]=0b10, bits[7:6]=0b10
        result = characteristic.parse_value(bytearray([0xA0]))
        expected = (
            DigitalSignalState.INACTIVE,
            DigitalSignalState.INACTIVE,
            DigitalSignalState.TRISTATE,
            DigitalSignalState.TRISTATE,
        )
        assert result == expected
