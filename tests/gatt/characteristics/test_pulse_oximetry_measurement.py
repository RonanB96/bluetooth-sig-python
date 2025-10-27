from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import PulseOximetryMeasurementCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.pulse_oximetry_measurement import (
    PulseOximetryData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPulseOximetryMeasurementCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return PulseOximetryMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        # Per Bluetooth SIG Assigned Numbers: 0x2A5F is PLX Continuous Measurement
        return "2A5F"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        from datetime import datetime

        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x80, 0x00, 0x80]),  # flags=0, SpO2=0, pulse_rate=0
                expected_value=PulseOximetryData(spo2=0.0, pulse_rate=0.0),
                description="Minimal pulse oximetry data (SpO2=0%, pulse=0 bpm)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x62, 0x80, 0x48, 0x80]),  # flags=0, SpO2=98%, pulse_rate=72 bpm
                expected_value=PulseOximetryData(spo2=98.0, pulse_rate=72.0),
                description="Normal pulse oximetry data (SpO2=98%, pulse=72 bpm)",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [0x01, 0x62, 0x80, 0x48, 0x80, 0xD0, 0x07, 0x01, 0x01, 0x00, 0x00, 0x00]
                ),  # flags=1, SpO2=98%, pulse_rate=72 bpm, timestamp=2000-01-01 00:00:00
                expected_value=PulseOximetryData(spo2=98.0, pulse_rate=72.0, timestamp=datetime(2000, 1, 1, 0, 0, 0)),
                description="Pulse oximetry with timestamp",
            ),
        ]
