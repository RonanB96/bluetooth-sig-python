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
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        # Example: Both wheel and crank data present
        # Flags: 0x03 (both present)
        # Cumulative Wheel Revolutions: 123456 (0x0001E240)
        # Last Wheel Event Time: 10240 (10.0s, 0x2800)
        # Cumulative Crank Revolutions: 321 (0x0141)
        # Last Crank Event Time: 2048 (2.0s, 0x0800)
        flags = CSCMeasurementFlags.WHEEL_REVOLUTION_DATA_PRESENT | CSCMeasurementFlags.CRANK_REVOLUTION_DATA_PRESENT
        wheel_revs = 123456
        wheel_time = 10240  # 10.0s in 1/1024s units
        crank_revs = 321
        crank_time = 2048  # 2.0s in 1/1024s units
        data = bytearray(
            [
                int(flags),
                *wheel_revs.to_bytes(4, "little"),
                *wheel_time.to_bytes(2, "little"),
                *crank_revs.to_bytes(2, "little"),
                *crank_time.to_bytes(2, "little"),
            ]
        )
        return CharacteristicTestData(
            input_data=data,
            expected_value=CSCMeasurementData(
                flags=flags,
                cumulative_wheel_revolutions=wheel_revs,
                last_wheel_event_time=wheel_time / 1024.0,
                cumulative_crank_revolutions=crank_revs,
                last_crank_event_time=crank_time / 1024.0,
            ),
            description="Both wheel and crank data present",
        )
