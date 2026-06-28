from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.cooking_common import (  # type: ignore[import-untyped]
    CookingConditionsData,
    CookingConditionsFlags,
)
from bluetooth_sig.gatt.characteristics.cooking_zone_desired_cooking_conditions import (  # type: ignore[import-untyped]
    CookingZoneDesiredCookingConditionsCharacteristic,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError, SpecialValueDetectedError
from bluetooth_sig.types import SpecialValueType

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCookingZoneDesiredCookingConditionsCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> CookingZoneDesiredCookingConditionsCharacteristic:
        return CookingZoneDesiredCookingConditionsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C2A"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                bytearray([0x0F, 0x00, 0x26, 0x02, 0xC8, 0x00, 0xD2, 0x0F, 0xA0]),
                CookingConditionsData(
                    flags=(
                        CookingConditionsFlags.POWER_LEVEL_PRESENT
                        | CookingConditionsFlags.TEMPERATURE_PRESENT
                        | CookingConditionsFlags.HUMIDITY_PRESENT
                        | CookingConditionsFlags.BLOWER_FAN_SPEED_PRESENT
                    ),
                    power_level=55.0,
                    temperature=20.0,
                    humidity=40.5,
                    blower_fan_speed=80.0,
                ),
                "all standard fields",
            ),
            CharacteristicTestData(
                bytearray([0x10, 0x00, 0xAA, 0xBB]),
                CookingConditionsData(
                    flags=CookingConditionsFlags.MANUFACTURER_DATA_PRESENT,
                    manufacturer_specific_data=b"\xaa\xbb",
                ),
                "manufacturer specific only",
            ),
        ]

    def test_short_payload_fails(self, characteristic: CookingZoneDesiredCookingConditionsCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x01]))

    def test_missing_temperature_when_flag_set_fails(
        self, characteristic: CookingZoneDesiredCookingConditionsCharacteristic
    ) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(CookingConditionsData(flags=CookingConditionsFlags.TEMPERATURE_PRESENT))

    def test_missing_manufacturer_data_when_flag_set_fails(
        self, characteristic: CookingZoneDesiredCookingConditionsCharacteristic
    ) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(CookingConditionsData(flags=CookingConditionsFlags.MANUFACTURER_DATA_PRESENT))

    def test_temperature_unknown_sentinel_raises_special_value(
        self, characteristic: CookingZoneDesiredCookingConditionsCharacteristic
    ) -> None:
        data = bytearray([0x02, 0x00, 0x00, 0x80])
        with pytest.raises(SpecialValueDetectedError) as exc_info:
            characteristic.parse_value(data)
        assert exc_info.value.special_value.value_type == SpecialValueType.UNKNOWN

    def test_humidity_unknown_sentinel_raises_special_value(
        self, characteristic: CookingZoneDesiredCookingConditionsCharacteristic
    ) -> None:
        with pytest.raises(SpecialValueDetectedError) as exc_info:
            characteristic.parse_value(bytearray([0x04, 0x00, 0xFF, 0xFF]))
        assert exc_info.value.special_value.value_type == SpecialValueType.UNKNOWN

    def test_rfu_flags_fail(self, characteristic: CookingZoneDesiredCookingConditionsCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x20, 0x00]))
