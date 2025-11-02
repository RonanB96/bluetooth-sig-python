from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import CSCMeasurementCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.csc_measurement import (
    CSCMeasurementCharacteristic,
    CSCMeasurementData,
    CSCMeasurementFlags,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCSCMeasurementCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return CSCMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A5B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        # Example 1: Both wheel and crank data present
        flags1 = CSCMeasurementFlags.WHEEL_REVOLUTION_DATA_PRESENT | CSCMeasurementFlags.CRANK_REVOLUTION_DATA_PRESENT
        wheel_revs1 = 123456
        wheel_time1 = 10240  # 10.0s in 1/1024s units
        crank_revs1 = 321
        crank_time1 = 2048  # 2.0s in 1/1024s units
        data1 = bytearray(
            [
                int(flags1),
                *wheel_revs1.to_bytes(4, "little"),
                *wheel_time1.to_bytes(2, "little"),
                *crank_revs1.to_bytes(2, "little"),
                *crank_time1.to_bytes(2, "little"),
            ]
        )

        # Example 2: Only wheel data present
        flags2 = CSCMeasurementFlags.WHEEL_REVOLUTION_DATA_PRESENT
        wheel_revs2 = 50000
        wheel_time2 = 5120  # 5.0s in 1/1024s units
        data2 = bytearray(
            [
                int(flags2),
                *wheel_revs2.to_bytes(4, "little"),
                *wheel_time2.to_bytes(2, "little"),
            ]
        )

        return [
            CharacteristicTestData(
                input_data=data1,
                expected_value=CSCMeasurementData(
                    flags=flags1,
                    cumulative_wheel_revolutions=wheel_revs1,
                    last_wheel_event_time=wheel_time1 / 1024.0,
                    cumulative_crank_revolutions=crank_revs1,
                    last_crank_event_time=crank_time1 / 1024.0,
                ),
                description="Both wheel and crank data present",
            ),
            CharacteristicTestData(
                input_data=data2,
                expected_value=CSCMeasurementData(
                    flags=flags2,
                    cumulative_wheel_revolutions=wheel_revs2,
                    last_wheel_event_time=wheel_time2 / 1024.0,
                    cumulative_crank_revolutions=None,
                    last_crank_event_time=None,
                ),
                description="Only wheel data present",
            ),
        ]
