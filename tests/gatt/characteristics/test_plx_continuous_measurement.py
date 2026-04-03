"""Test PLX Continuous Measurement characteristic (0x2A5F) per PLXS v1.0.1."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.plx_continuous_measurement import (
    PLXContinuousData,
    PLXContinuousFlags,
    PLXContinuousMeasurementCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPLXContinuousMeasurementCharacteristic(CommonCharacteristicTests):
    """Test PLX Continuous Measurement characteristic (0x2A5F) per PLXS v1.0.1."""

    @pytest.fixture
    def characteristic(self) -> PLXContinuousMeasurementCharacteristic:
        return PLXContinuousMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A5F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            # Test 1: Minimal — SpO2PR-Normal only (no optional fields)
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x62, 0x80, 0x48, 0x80]),
                expected_value=PLXContinuousData(
                    continuous_flags=PLXContinuousFlags(0),
                    spo2=98.0,
                    pulse_rate=72.0,
                ),
                description="Minimal continuous (SpO2=98%, pulse=72 bpm, normal only)",
            ),
            # Test 2: With SpO2PR-Fast (bit 0)
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x62, 0x80, 0x48, 0x80, 0x61, 0x80, 0x4B, 0x80]),
                expected_value=PLXContinuousData(
                    continuous_flags=PLXContinuousFlags.SPO2PR_FAST_PRESENT,
                    spo2=98.0,
                    pulse_rate=72.0,
                    spo2_fast=97.0,
                    pulse_rate_fast=75.0,
                ),
                description="Continuous with SpO2PR-Fast (fast SpO2=97%, fast PR=75 bpm)",
            ),
            # Test 3: With SpO2PR-Slow (bit 1)
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x62, 0x80, 0x48, 0x80, 0x63, 0x80, 0x46, 0x80]),
                expected_value=PLXContinuousData(
                    continuous_flags=PLXContinuousFlags.SPO2PR_SLOW_PRESENT,
                    spo2=98.0,
                    pulse_rate=72.0,
                    spo2_slow=99.0,
                    pulse_rate_slow=70.0,
                ),
                description="Continuous with SpO2PR-Slow (slow SpO2=99%, slow PR=70 bpm)",
            ),
        ]
