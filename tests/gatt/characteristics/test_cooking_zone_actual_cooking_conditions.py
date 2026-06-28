from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.cooking_common import (  # type: ignore[import-untyped]
    CookingConditionsData,
    CookingConditionsFlags,
)
from bluetooth_sig.gatt.characteristics.cooking_zone_actual_cooking_conditions import (  # type: ignore[import-untyped]
    CookingZoneActualCookingConditionsCharacteristic,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError, SpecialValueDetectedError
from bluetooth_sig.types import SpecialValueType

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCookingZoneActualCookingConditionsCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> CookingZoneActualCookingConditionsCharacteristic:
        return CookingZoneActualCookingConditionsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C2B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                bytearray([0x03, 0x00, 0x58, 0x02, 0x9B, 0x00]),
                CookingConditionsData(
                    flags=CookingConditionsFlags.POWER_LEVEL_PRESENT | CookingConditionsFlags.TEMPERATURE_PRESENT,
                    power_level=60.0,
                    temperature=15.5,
                ),
                "power + temperature",
            ),
            CharacteristicTestData(
                bytearray([0x10, 0x00, 0x01, 0x02, 0x03]),
                CookingConditionsData(
                    flags=CookingConditionsFlags.MANUFACTURER_DATA_PRESENT,
                    manufacturer_specific_data=b"\x01\x02\x03",
                ),
                "manufacturer only",
            ),
        ]

    def test_short_payload_fails(self, characteristic: CookingZoneActualCookingConditionsCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x10]))

    def test_missing_power_level_when_flag_set_fails(
        self, characteristic: CookingZoneActualCookingConditionsCharacteristic
    ) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(CookingConditionsData(flags=CookingConditionsFlags.POWER_LEVEL_PRESENT))

    def test_missing_manufacturer_data_when_flag_set_fails(
        self, characteristic: CookingZoneActualCookingConditionsCharacteristic
    ) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(CookingConditionsData(flags=CookingConditionsFlags.MANUFACTURER_DATA_PRESENT))

    def test_temperature_unknown_sentinel_raises_special_value(
        self, characteristic: CookingZoneActualCookingConditionsCharacteristic
    ) -> None:
        with pytest.raises(SpecialValueDetectedError) as exc_info:
            characteristic.parse_value(bytearray([0x02, 0x00, 0x00, 0x80]))
        assert exc_info.value.special_value.value_type == SpecialValueType.UNKNOWN

    def test_humidity_unknown_sentinel_raises_special_value(
        self, characteristic: CookingZoneActualCookingConditionsCharacteristic
    ) -> None:
        with pytest.raises(SpecialValueDetectedError) as exc_info:
            characteristic.parse_value(bytearray([0x04, 0x00, 0xFF, 0xFF]))
        assert exc_info.value.special_value.value_type == SpecialValueType.UNKNOWN

    def test_rfu_flags_fail(self, characteristic: CookingZoneActualCookingConditionsCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x20, 0x00]))
