from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.cooking_zone_perceived_power import (  # type: ignore[import-untyped]
    CookingZonePerceivedPowerCharacteristic,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCookingZonePerceivedPowerCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> CookingZonePerceivedPowerCharacteristic:
        return CookingZonePerceivedPowerCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C2F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0xE8, 0x03]), 100.0, "100%"),
            CharacteristicTestData(bytearray([0xDE, 0x0D]), 355.0, "355%"),
        ]

    def test_short_payload_fails(self, characteristic: CookingZonePerceivedPowerCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x00]))

    def test_out_of_range_build_fails(self, characteristic: CookingZonePerceivedPowerCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(7000.0)
