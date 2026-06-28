from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.cookware_sensor_aggregate import (  # type: ignore[import-untyped]
    CookwareSensorAggregateCharacteristic,
    CookwareSensorAggregateValue,
)

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
                bytearray([0x00, 0xAA, 0xBB, 0xCC]),
                CookwareSensorAggregateValue(aggregate_data=b"\x00\xaa\xbb\xcc"),
                "aggregate payload",
            ),
            CharacteristicTestData(
                bytearray(),
                CookwareSensorAggregateValue(aggregate_data=b""),
                "empty aggregate payload",
            ),
        ]
