from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import BodyCompositionFeatureCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.body_composition_feature import (
    BodyCompositionFeatureData,
    BodyCompositionFeatures,
    HeightMeasurementResolution,
    MassMeasurementResolution,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBodyCompositionFeatureCharacteristic(CommonCharacteristicTests):
    characteristic_cls = BodyCompositionFeatureCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return BodyCompositionFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A9B"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),  # No features supported
                expected_value=BodyCompositionFeatureData(
                    features=BodyCompositionFeatures(0),
                    timestamp_supported=False,
                    multiple_users_supported=False,
                    basal_metabolism_supported=False,
                    muscle_mass_supported=False,
                    muscle_percentage_supported=False,
                    fat_free_mass_supported=False,
                    soft_lean_mass_supported=False,
                    body_water_mass_supported=False,
                    impedance_supported=False,
                    weight_supported=False,
                    height_supported=False,
                    mass_measurement_resolution=MassMeasurementResolution.NOT_SPECIFIED,
                    height_measurement_resolution=HeightMeasurementResolution.NOT_SPECIFIED,
                ),
                description="No features supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0x0F, 0x00, 0x00]),  # All basic features supported, mass resolution = 1
                expected_value=BodyCompositionFeatureData(
                    features=BodyCompositionFeatures(0x0FFF),
                    timestamp_supported=True,
                    multiple_users_supported=True,
                    basal_metabolism_supported=True,
                    muscle_mass_supported=True,
                    muscle_percentage_supported=True,
                    fat_free_mass_supported=True,
                    soft_lean_mass_supported=True,
                    body_water_mass_supported=True,
                    impedance_supported=True,
                    weight_supported=True,
                    height_supported=True,
                    mass_measurement_resolution=MassMeasurementResolution.KG_0_5_OR_LB_1,
                    height_measurement_resolution=HeightMeasurementResolution.NOT_SPECIFIED,
                ),
                description="All basic features supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x20, 0x01, 0x00]),  # Mass resolution 0.05kg, height resolution 0.005m
                expected_value=BodyCompositionFeatureData(
                    features=BodyCompositionFeatures(0x12000),
                    timestamp_supported=False,
                    multiple_users_supported=False,
                    basal_metabolism_supported=False,
                    muscle_mass_supported=False,
                    muscle_percentage_supported=False,
                    fat_free_mass_supported=False,
                    soft_lean_mass_supported=False,
                    body_water_mass_supported=False,
                    impedance_supported=False,
                    weight_supported=False,
                    height_supported=False,
                    mass_measurement_resolution=MassMeasurementResolution.KG_0_05_OR_LB_0_1,
                    height_measurement_resolution=HeightMeasurementResolution.M_0_005_OR_INCH_0_5,
                ),
                description="High resolution measurements",
            ),
        ]
