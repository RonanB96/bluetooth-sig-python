from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import HeartRateMeasurementCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.heart_rate_measurement import (
    HeartRateData,
    HeartRateMeasurementFlags,
    SensorContactState,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHeartRateMeasurementCharacteristic(CommonCharacteristicTests):
    characteristic_cls = HeartRateMeasurementCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return HeartRateMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A37"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x50]),  # Flags=0, HR=80 BPM (8-bit)
                expected_value=HeartRateData(
                    heart_rate=80,
                    sensor_contact=SensorContactState.NOT_SUPPORTED,
                    energy_expended=None,
                    rr_intervals=(),
                    flags=HeartRateMeasurementFlags(0),
                ),
                description="Basic 8-bit heart rate",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0xC8, 0x00]),  # Flags=1 (16-bit HR), HR=200 BPM
                expected_value=HeartRateData(
                    heart_rate=200,
                    sensor_contact=SensorContactState.NOT_SUPPORTED,
                    energy_expended=None,
                    rr_intervals=(),
                    flags=HeartRateMeasurementFlags.HEART_RATE_VALUE_FORMAT_UINT16,
                ),
                description="16-bit heart rate",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [0x0E, 0x4B, 0x80, 0x00]
                ),  # Flags=14 (sensor contact detected + energy), HR=75, Energy=128 kJ
                expected_value=HeartRateData(
                    heart_rate=75,
                    sensor_contact=SensorContactState.DETECTED,
                    energy_expended=128,
                    rr_intervals=(),
                    flags=HeartRateMeasurementFlags.SENSOR_CONTACT_SUPPORTED
                    | HeartRateMeasurementFlags.SENSOR_CONTACT_DETECTED
                    | HeartRateMeasurementFlags.ENERGY_EXPENDED_PRESENT,
                ),
                description="Sensor contact detected with energy expended",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [0x10, 0x5A, 0x00, 0x08, 0x00, 0x10]
                ),  # Flags=16 (RR intervals), HR=90, RR=2.0s (2048/1024), 4.0s (4096/1024)
                expected_value=HeartRateData(
                    heart_rate=90,
                    sensor_contact=SensorContactState.NOT_SUPPORTED,
                    energy_expended=None,
                    rr_intervals=(2.0, 4.0),
                    flags=HeartRateMeasurementFlags.RR_INTERVAL_PRESENT,
                ),
                description="Heart rate with RR intervals",
            ),
        ]
