"""Test Uncertainty characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import UncertaintyCharacteristic
from bluetooth_sig.gatt.characteristics.uncertainty import UncertaintyData
from bluetooth_sig.gatt.exceptions import CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestUncertaintyCharacteristic(CommonCharacteristicTests):
    """Test Uncertainty characteristic implementation per IPS v1.0 §3.8."""

    @pytest.fixture
    def characteristic(self) -> UncertaintyCharacteristic:
        return UncertaintyCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AB4"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid Uncertainty test data per IPS v1.0 §3.8 bitfield encoding.

        Byte layout: bit 0 = stationary, bits 1-3 = update time index, bits 4-6 = precision index.
        Lookup table for both: (1, 4, 5, 7, 10, 14, 20, 28).
        """
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=UncertaintyData(stationary=False, update_time=1, precision=1),
                description="Stationary, fastest update, best precision",
            ),
            CharacteristicTestData(
                # bit0=1(mobile), bits1-3=0b010(idx2→5s), bits4-6=0b011(idx3→7dm)
                # 0b_0_011_010_1 = 0x35
                input_data=bytearray([0x35]),
                expected_value=UncertaintyData(stationary=True, update_time=5, precision=7),
                description="Mobile, 5s update, 7dm precision",
            ),
            CharacteristicTestData(
                # bit0=0, bits1-3=0b111(idx7→28s), bits4-6=0b111(idx7→28dm)
                # 0b_0_111_111_0 = 0x7E
                input_data=bytearray([0x7E]),
                expected_value=UncertaintyData(stationary=False, update_time=28, precision=28),
                description="Stationary, slowest update, worst precision",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x59]),
                expected_value=UncertaintyData(stationary=True, update_time=10, precision=14),
                description="Stationary, 10s update, 14dm precision",
            ),
        ]

    def test_uncertainty_error_handling(self, characteristic: UncertaintyCharacteristic) -> None:
        """Test Uncertainty error handling."""
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([]))

    def test_uncertainty_all_lookup_values(self, characteristic: UncertaintyCharacteristic) -> None:
        """Verify all 8 lookup entries decode correctly."""
        lookup = (1, 4, 5, 7, 10, 14, 20, 28)
        for idx, expected_val in enumerate(lookup):
            # Set update_time index in bits 1-3
            raw = (idx & 0x07) << 1
            result = characteristic.parse_value(bytearray([raw]))
            assert result.update_time == expected_val
