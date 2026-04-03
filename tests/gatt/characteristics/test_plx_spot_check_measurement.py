"""Tests for PLXSpotCheckMeasurementCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.plx_features import PLXFeatureFlags, PLXFeaturesCharacteristic
from bluetooth_sig.gatt.characteristics.plx_spot_check_measurement import (
    PLXMeasurementStatus,
    PLXSpotCheckData,
    PLXSpotCheckFlags,
    PLXSpotCheckMeasurementCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
    DependencyTestData,
)


class TestPLXSpotCheckMeasurementCharacteristic(CommonCharacteristicTests):
    """PLXSpotCheckMeasurementCharacteristic test suite."""

    @pytest.fixture
    def characteristic(self) -> PLXSpotCheckMeasurementCharacteristic:
        return PLXSpotCheckMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A5E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        # SFLOAT: integer values have exponent_raw=8 (bias), high nibble=0x8
        # 98.0 -> LE [0x62, 0x80]; 72.0 -> LE [0x48, 0x80]
        # 95.0 -> LE [0x5F, 0x80]; 60.0 -> LE [0x3C, 0x80]
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x62, 0x80, 0x48, 0x80]),
                expected_value=PLXSpotCheckData(
                    spot_check_flags=PLXSpotCheckFlags(0),
                    spo2=98.0,
                    pulse_rate=72.0,
                ),
                description="Basic SpO2 98%, pulse 72 bpm, no optional fields",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x02,  # flags: MEASUREMENT_STATUS_PRESENT
                        0x5F,
                        0x80,  # SpO2 95.0
                        0x3C,
                        0x80,  # Pulse rate 60.0
                        0x80,
                        0x00,  # Measurement status: VALIDATED_DATA (bit 7 = 0x0080)
                    ]
                ),
                expected_value=PLXSpotCheckData(
                    spot_check_flags=PLXSpotCheckFlags.MEASUREMENT_STATUS_PRESENT,
                    spo2=95.0,
                    pulse_rate=60.0,
                    measurement_status=PLXMeasurementStatus.VALIDATED_DATA,
                ),
                description="SpO2 95%, pulse 60 bpm with measurement status",
            ),
        ]

    @pytest.fixture
    def dependency_test_data(self) -> list[DependencyTestData]:
        """Test data for optional PLX Features dependency."""
        spot_check_data = bytearray([0x00, 0x62, 0x80, 0x48, 0x80])
        spot_check_uuid = str(PLXSpotCheckMeasurementCharacteristic.get_class_uuid())
        plx_features_uuid = str(PLXFeaturesCharacteristic.get_class_uuid())
        plx_features_data = bytearray([0x01, 0x00])  # MEASUREMENT_STATUS_SUPPORT

        return [
            DependencyTestData(
                with_dependency_data={
                    spot_check_uuid: spot_check_data,
                    plx_features_uuid: plx_features_data,
                },
                without_dependency_data=spot_check_data,
                expected_with=PLXSpotCheckData(
                    spot_check_flags=PLXSpotCheckFlags(0),
                    spo2=98.0,
                    pulse_rate=72.0,
                    supported_features=PLXFeatureFlags.MEASUREMENT_STATUS_SUPPORT,
                ),
                expected_without=PLXSpotCheckData(
                    spot_check_flags=PLXSpotCheckFlags(0),
                    spo2=98.0,
                    pulse_rate=72.0,
                ),
                description="PLX Features optional dependency",
            ),
        ]
