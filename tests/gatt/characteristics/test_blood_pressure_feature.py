from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import BloodPressureFeatureCharacteristic
from bluetooth_sig.gatt.characteristics.blood_pressure_feature import BloodPressureFeatureData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBloodPressureFeatureCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BloodPressureFeatureCharacteristic:
        return BloodPressureFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        # Per SIG registry: org.bluetooth.characteristic.blood_pressure_feature = 2A49
        return "2A49"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        # 0x0000: all features off; 0x003F: all features on; 0x0001: only body movement detection
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=BloodPressureFeatureData(
                    features_bitmap=0,
                    body_movement_detection_support=False,
                    cuff_fit_detection_support=False,
                    irregular_pulse_detection_support=False,
                    pulse_rate_range_detection_support=False,
                    measurement_position_detection_support=False,
                    multiple_bond_support=False,
                ),
                description="No features supported (all bits 0)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x3F, 0x00]),
                expected_value=BloodPressureFeatureData(
                    features_bitmap=0x3F,
                    body_movement_detection_support=True,
                    cuff_fit_detection_support=True,
                    irregular_pulse_detection_support=True,
                    pulse_rate_range_detection_support=True,
                    measurement_position_detection_support=True,
                    multiple_bond_support=True,
                ),
                description="All features supported (all bits 1)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=BloodPressureFeatureData(
                    features_bitmap=0x01,
                    body_movement_detection_support=True,
                    cuff_fit_detection_support=False,
                    irregular_pulse_detection_support=False,
                    pulse_rate_range_detection_support=False,
                    measurement_position_detection_support=False,
                    multiple_bond_support=False,
                ),
                description="Only body movement detection supported",
            ),
        ]
