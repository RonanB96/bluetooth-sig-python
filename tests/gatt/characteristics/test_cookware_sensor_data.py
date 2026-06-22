from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.cookware_sensor_data import (  # type: ignore[import-untyped]
    CookwareSensorDataCharacteristic,
    CookwareSensorDataValue,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCookwareSensorDataCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> CookwareSensorDataCharacteristic:
        return CookwareSensorDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C2C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                bytearray([0x01, 0x00, 0x10, 0x20]),
                CookwareSensorDataValue(flags=1, sensor_payload=b"\x10\x20"),
                "flags + payload",
            ),
            CharacteristicTestData(
                bytearray([0x00, 0x00]),
                CookwareSensorDataValue(flags=0, sensor_payload=b""),
                "flags only",
            ),
        ]

    def test_short_payload_fails(self, characteristic: CookwareSensorDataCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x00]))

    def test_flag_overflow_build_fails(self, characteristic: CookwareSensorDataCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(CookwareSensorDataValue(flags=0x1_0000, sensor_payload=b""))
