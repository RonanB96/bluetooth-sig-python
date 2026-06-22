from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.cookware_sensor_aggregate import (  # type: ignore[import-untyped]
    CookwareSensorAggregateCharacteristic,
    CookwareSensorAggregateValue,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCookwareSensorAggregateCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> CookwareSensorAggregateCharacteristic:
        return CookwareSensorAggregateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C2D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                bytearray([0x03, 0x00, 0xAA, 0xBB, 0xCC]),
                CookwareSensorAggregateValue(flags=3, aggregate_payload=b"\xaa\xbb\xcc"),
                "aggregate payload",
            ),
            CharacteristicTestData(
                bytearray([0x00, 0x00]),
                CookwareSensorAggregateValue(flags=0, aggregate_payload=b""),
                "empty aggregate payload",
            ),
        ]

    def test_short_payload_fails(self, characteristic: CookwareSensorAggregateCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x01]))

    def test_flag_overflow_build_fails(self, characteristic: CookwareSensorAggregateCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(CookwareSensorAggregateValue(flags=0x1_0000, aggregate_payload=b""))
