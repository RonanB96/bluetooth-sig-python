from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import WeightScaleFeatureCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.weight_scale_feature import (
    HeightMeasurementResolution,
    WeightMeasurementResolution,
    WeightScaleFeatureData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestWeightScaleFeatureCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return WeightScaleFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        # Per Bluetooth SIG Assigned Numbers: 0x2A9E is Weight Scale Feature
        return "2A9E"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),  # No features
                expected_value=WeightScaleFeatureData(
                    raw_value=0,
                    timestamp_supported=False,
                    multiple_users_supported=False,
                    bmi_supported=False,
                    weight_measurement_resolution=WeightMeasurementResolution.NOT_SPECIFIED,
                    height_measurement_resolution=HeightMeasurementResolution.NOT_SPECIFIED,
                ),
                description="No features supported",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [0x07, 0x00, 0x00, 0x00]
                ),  # All basic features: 0x07 = timestamp + multiple users + BMI
                expected_value=WeightScaleFeatureData(
                    raw_value=7,
                    timestamp_supported=True,
                    multiple_users_supported=True,
                    bmi_supported=True,
                    weight_measurement_resolution=WeightMeasurementResolution.NOT_SPECIFIED,
                    height_measurement_resolution=HeightMeasurementResolution.NOT_SPECIFIED,
                ),
                description="All basic features supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x8F, 0x00, 0x00, 0x00]),  # Features + resolutions: weight=0.5kg, height=0.01m
                expected_value=WeightScaleFeatureData(
                    raw_value=0x0000008F,
                    timestamp_supported=True,
                    multiple_users_supported=True,
                    bmi_supported=True,
                    weight_measurement_resolution=WeightMeasurementResolution.HALF_KG_OR_1_LB,
                    height_measurement_resolution=HeightMeasurementResolution.POINT_01_M_OR_1_INCH,
                ),
                description="Features with high resolution settings",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x08, 0x00, 0x00, 0x00]),  # Only weight resolution: 0.5kg
                expected_value=WeightScaleFeatureData(
                    raw_value=0x00000008,
                    timestamp_supported=False,
                    multiple_users_supported=False,
                    bmi_supported=False,
                    weight_measurement_resolution=WeightMeasurementResolution.HALF_KG_OR_1_LB,
                    height_measurement_resolution=HeightMeasurementResolution.NOT_SPECIFIED,
                ),
                description="Only weight resolution specified",
            ),
        ]
