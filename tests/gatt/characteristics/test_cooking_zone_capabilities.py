from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.cooking_zone_capabilities import (  # type: ignore[import-untyped]
    CookingZoneCapabilitiesCharacteristic,
    CookingZoneCapabilitiesData,
    CookingZoneCapabilitiesFlags,
    PowerTechnology,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError, SpecialValueDetectedError
from bluetooth_sig.types import SpecialValueType

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCookingZoneCapabilitiesCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> CookingZoneCapabilitiesCharacteristic:
        return CookingZoneCapabilitiesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C29"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        flags = (
            CookingZoneCapabilitiesFlags.POWER_CONTROL_SUPPORTED
            | CookingZoneCapabilitiesFlags.TEMPERATURE_CONTROL_SUPPORTED
            | CookingZoneCapabilitiesFlags.BLOWER_FAN_AIRFLOW_SUPPORTED
        )
        return [
            CharacteristicTestData(
                bytearray(
                    [
                        0x16,
                        0x00,
                        0x01,
                        0x05,
                        0x00,
                        0xA0,
                        0x86,
                        0x01,
                        0x78,
                        0xF4,
                        0x01,
                        0xFA,
                        0x00,
                        0xB4,
                        0x00,
                        0xDC,
                        0x05,
                    ]
                ),
                CookingZoneCapabilitiesData(
                    flags=flags,
                    power_technology=PowerTechnology.HEATING_INDUCTION,
                    number_of_cooking_steps=5,
                    nominal_power=10000.0,
                    boost_level_percent=120,
                    minimum_available_power=50.0,
                    maximum_temperature=25.0,
                    minimum_temperature=18.0,
                    maximum_blower_fan_airflow=1.5,
                ),
                "all optional groups present",
            ),
            CharacteristicTestData(
                bytearray([0x00, 0x00, 0x00, 0x00, 0x00]),
                CookingZoneCapabilitiesData(
                    flags=CookingZoneCapabilitiesFlags(0),
                    power_technology=PowerTechnology.UNKNOWN_OR_OTHER,
                    number_of_cooking_steps=0,
                ),
                "minimal payload",
            ),
        ]

    def test_short_payload_fails(self, characteristic: CookingZoneCapabilitiesCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x00, 0x00, 0x00]))

    def test_missing_power_fields_for_build_fails(self, characteristic: CookingZoneCapabilitiesCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(
                CookingZoneCapabilitiesData(
                    flags=CookingZoneCapabilitiesFlags.POWER_CONTROL_SUPPORTED,
                    power_technology=PowerTechnology.HEATING_INDUCTION,
                    number_of_cooking_steps=2,
                )
            )

    def test_rfu_flags_fail(self, characteristic: CookingZoneCapabilitiesCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x40, 0x00, 0x01, 0x01, 0x00]))

    def test_temperature_unknown_sentinel_raises_special_value(
        self, characteristic: CookingZoneCapabilitiesCharacteristic
    ) -> None:
        with pytest.raises(SpecialValueDetectedError) as exc_info:
            characteristic.parse_value(bytearray([0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80]))
        assert exc_info.value.special_value.value_type == SpecialValueType.UNKNOWN
