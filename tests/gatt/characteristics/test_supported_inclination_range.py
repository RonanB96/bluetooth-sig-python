"""Tests for SupportedInclinationRangeCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import SupportedInclinationRangeCharacteristic
from bluetooth_sig.gatt.characteristics.supported_inclination_range import (
    SupportedInclinationRangeData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSupportedInclinationRangeCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> SupportedInclinationRangeCharacteristic:
        return SupportedInclinationRangeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AD5"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=SupportedInclinationRangeData(
                    minimum=0.0,
                    maximum=0.0,
                    minimum_increment=0.0,
                ),
                description="Zero inclination range",
            ),
            CharacteristicTestData(
                # min=-15.0% (raw -150=0xFF6A as sint16 LE: 0x6A, 0xFF)
                # max=15.0% (raw 150=0x0096)
                # inc=0.5% (raw 5=0x0005)
                input_data=bytearray([0x6A, 0xFF, 0x96, 0x00, 0x05, 0x00]),
                expected_value=SupportedInclinationRangeData(
                    minimum=-15.0,
                    maximum=15.0,
                    minimum_increment=0.5,
                ),
                description="Treadmill inclination range (-15% to +15%, 0.5% step)",
            ),
            CharacteristicTestData(
                # max positive sint16: 32767 -> 3276.7%
                # max uint16 increment: 65535 -> 6553.5%
                input_data=bytearray([0x00, 0x80, 0xFF, 0x7F, 0xFF, 0xFF]),
                expected_value=SupportedInclinationRangeData(
                    minimum=-3276.8,
                    maximum=3276.7,
                    minimum_increment=6553.5,
                ),
                description="Full range (sint16 min/max, uint16 max increment)",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = SupportedInclinationRangeCharacteristic()
        original = SupportedInclinationRangeData(
            minimum=-10.0,
            maximum=15.0,
            minimum_increment=0.5,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_validation_rejects_inverted_range(self) -> None:
        """Minimum > maximum is invalid."""
        with pytest.raises(ValueError, match="cannot be greater"):
            SupportedInclinationRangeData(minimum=15.0, maximum=-5.0, minimum_increment=0.5)

    def test_negative_inclination_allowed(self) -> None:
        """Negative inclination (decline) is valid for sint16."""
        data = SupportedInclinationRangeData(minimum=-20.0, maximum=-5.0, minimum_increment=1.0)
        assert data.minimum == -20.0
        assert data.maximum == -5.0
