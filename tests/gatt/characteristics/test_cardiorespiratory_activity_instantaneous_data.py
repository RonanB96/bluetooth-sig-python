"""Tests for CardioRespiratory Activity Instantaneous Data characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.cardiorespiratory_activity_instantaneous_data import (
    CardioRespiratoryActivityInstantaneousData,
    CardioRespiratoryActivityInstantaneousDataCharacteristic,
    CardioRespiratoryInstantaneousFlags,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCardioRespiratoryActivityInstantaneousDataCharacteristic(CommonCharacteristicTests):
    """Test suite for CardioRespiratory Activity Instantaneous Data."""

    @pytest.fixture
    def characteristic(self) -> CardioRespiratoryActivityInstantaneousDataCharacteristic:
        return CardioRespiratoryActivityInstantaneousDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B3E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=CardioRespiratoryActivityInstantaneousData(
                    flags=CardioRespiratoryInstantaneousFlags(0x0000),
                    additional_data=b"",
                ),
                description="No optional fields present (flags=0)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x00, 0x48, 0x50]),
                expected_value=CardioRespiratoryActivityInstantaneousData(
                    flags=CardioRespiratoryInstantaneousFlags(0x0003),
                    additional_data=b"\x48\x50",
                ),
                description="Flags 0x0003 with additional activity data",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = CardioRespiratoryActivityInstantaneousDataCharacteristic()
        data = CardioRespiratoryActivityInstantaneousData(
            flags=CardioRespiratoryInstantaneousFlags(0x0005), additional_data=b"\x01\x02\x03"
        )
        encoded = char.build_value(data)
        decoded = char.parse_value(encoded)
        assert decoded == data
