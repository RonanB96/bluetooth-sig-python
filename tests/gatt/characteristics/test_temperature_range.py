from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import TemperatureRangeCharacteristic
from bluetooth_sig.gatt.characteristics.temperature_range import TemperatureRangeData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTemperatureRangeCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> TemperatureRangeCharacteristic:
        return TemperatureRangeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B10"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=TemperatureRangeData(minimum=0.0, maximum=0.0),
                description="Zero temperature range",
            ),
            CharacteristicTestData(
                # min = 20.00°C → raw 2000 (0x07D0), max = 25.00°C → raw 2500 (0x09C4)
                input_data=bytearray([0xD0, 0x07, 0xC4, 0x09]),
                expected_value=TemperatureRangeData(minimum=20.0, maximum=25.0),
                description="Room temperature range (20-25°C)",
            ),
            CharacteristicTestData(
                # min = -10.00°C → raw -1000 (0xFC18), max = 40.00°C → raw 4000 (0x0FA0)
                input_data=bytearray([0x18, 0xFC, 0xA0, 0x0F]),
                expected_value=TemperatureRangeData(minimum=-10.0, maximum=40.0),
                description="Wide range with negative minimum",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = TemperatureRangeCharacteristic()
        original = TemperatureRangeData(minimum=-5.5, maximum=35.75)
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert abs(decoded.minimum - original.minimum) < 0.01
        assert abs(decoded.maximum - original.maximum) < 0.01

    def test_validation_rejects_inverted_range(self) -> None:
        """Minimum > maximum is invalid."""
        with pytest.raises(ValueError, match="cannot be greater"):
            TemperatureRangeData(minimum=30.0, maximum=20.0)
