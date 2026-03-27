"""Tests for Sink ASE characteristic (0x2BC4)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.sink_ase import (
    ASEState,
    SinkASECharacteristic,
    SinkASEData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSinkASECharacteristic(CommonCharacteristicTests):
    """Test suite for Sink ASE characteristic."""

    @pytest.fixture
    def characteristic(self) -> SinkASECharacteristic:
        return SinkASECharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BC4"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=SinkASEData(
                    ase_id=1,
                    ase_state=ASEState.IDLE,
                    additional_data=b"",
                ),
                description="ASE ID 1, Idle state, no additional data",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x04, 0xAA, 0xBB]),
                expected_value=SinkASEData(
                    ase_id=3,
                    ase_state=ASEState.STREAMING,
                    additional_data=b"\xaa\xbb",
                ),
                description="ASE ID 3, Streaming state, with additional data",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05, 0x06]),
                expected_value=SinkASEData(
                    ase_id=5,
                    ase_state=ASEState.RELEASING,
                    additional_data=b"",
                ),
                description="ASE ID 5, Releasing state",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = SinkASECharacteristic()
        original = SinkASEData(
            ase_id=2,
            ase_state=ASEState.CODEC_CONFIGURED,
            additional_data=b"\x01\x02\x03",
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
