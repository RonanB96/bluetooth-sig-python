"""Tests for Energy in a Period of Day characteristic (0x2AF3)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import EnergyInAPeriodOfDayCharacteristic
from bluetooth_sig.gatt.characteristics.energy_in_a_period_of_day import (
    EnergyInAPeriodOfDayData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestEnergyInAPeriodOfDayCharacteristic(CommonCharacteristicTests):
    """Test suite for Energy in a Period of Day characteristic."""

    @pytest.fixture
    def characteristic(self) -> EnergyInAPeriodOfDayCharacteristic:
        return EnergyInAPeriodOfDayCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AF3"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=EnergyInAPeriodOfDayData(
                    energy=0,
                    start_time=0.0,
                    end_time=0.0,
                ),
                description="Zero energy, midnight to midnight",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0A, 0x00, 0x00, 0x3C, 0xB4]),
                expected_value=EnergyInAPeriodOfDayData(
                    energy=10,
                    start_time=6.0,
                    end_time=18.0,
                ),
                description="10 kWh from 06:00 to 18:00",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = EnergyInAPeriodOfDayCharacteristic()
        original = EnergyInAPeriodOfDayData(
            energy=500,
            start_time=8.0,
            end_time=17.0,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_validation_rejects_negative_energy(self) -> None:
        """Negative energy is invalid for uint24."""
        with pytest.raises(ValueError, match="outside valid range"):
            EnergyInAPeriodOfDayData(energy=-1, start_time=0.0, end_time=0.0)
