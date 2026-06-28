from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.kitchen_appliance_airflow import (  # type: ignore[import-untyped]
    KitchenApplianceAirflowCharacteristic,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError, SpecialValueDetectedError
from bluetooth_sig.types import SpecialValueType

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestKitchenApplianceAirflowCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> KitchenApplianceAirflowCharacteristic:
        return KitchenApplianceAirflowCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C30"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0xE8, 0x03]), 1.0, "1.0 m^3/s"),
            CharacteristicTestData(bytearray([0x00, 0x00]), 0.0, "0 airflow"),
        ]

    def test_short_payload_fails(self, characteristic: KitchenApplianceAirflowCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x00]))

    def test_out_of_range_build_fails(self, characteristic: KitchenApplianceAirflowCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(1000.0)

    def test_unknown_sentinel_raises_special_value(self, characteristic: KitchenApplianceAirflowCharacteristic) -> None:
        with pytest.raises(SpecialValueDetectedError) as exc_info:
            characteristic.parse_value(bytearray([0xFF, 0xFF]))
        assert exc_info.value.special_value.value_type == SpecialValueType.UNKNOWN
