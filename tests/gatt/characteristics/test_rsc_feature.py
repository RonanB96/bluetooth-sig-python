from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import BaseCharacteristic, RSCFeatureCharacteristic
from bluetooth_sig.gatt.characteristics.rsc_feature import RSCFeatureData, RSCFeatures

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRSCFeatureCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return RSCFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        # Per Bluetooth SIG Assigned Numbers: 0x2A54 is RSC Feature
        return "2A54"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),  # No features supported
                expected_value=RSCFeatureData(
                    features=RSCFeatures(0),
                    instantaneous_stride_length_supported=False,
                    total_distance_supported=False,
                    walking_or_running_status_supported=False,
                    calibration_procedure_supported=False,
                    multiple_sensor_locations_supported=False,
                ),
                description="No features supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x1F, 0x00]),  # All features supported (0x001F)
                expected_value=RSCFeatureData(
                    features=RSCFeatures.INSTANTANEOUS_STRIDE_LENGTH_SUPPORTED
                    | RSCFeatures.TOTAL_DISTANCE_SUPPORTED
                    | RSCFeatures.WALKING_OR_RUNNING_STATUS_SUPPORTED
                    | RSCFeatures.CALIBRATION_PROCEDURE_SUPPORTED
                    | RSCFeatures.MULTIPLE_SENSOR_LOCATIONS_SUPPORTED,
                    instantaneous_stride_length_supported=True,
                    total_distance_supported=True,
                    walking_or_running_status_supported=True,
                    calibration_procedure_supported=True,
                    multiple_sensor_locations_supported=True,
                ),
                description="All features supported",
            ),
        ]
