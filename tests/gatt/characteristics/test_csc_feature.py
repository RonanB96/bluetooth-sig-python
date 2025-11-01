from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import CSCFeatureCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.csc_feature import CSCFeatureData, CSCFeatures

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCSCFeatureCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return CSCFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A5C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        # Example: Wheel and Crank Revolution Data Supported (0x03)
        bitmask1 = CSCFeatures.WHEEL_REVOLUTION_DATA_SUPPORTED | CSCFeatures.CRANK_REVOLUTION_DATA_SUPPORTED
        bitmask2 = CSCFeatures.WHEEL_REVOLUTION_DATA_SUPPORTED | CSCFeatures.MULTIPLE_SENSOR_LOCATIONS_SUPPORTED
        return [
            CharacteristicTestData(
                input_data=bytearray(bitmask1.to_bytes(2, "little")),
                expected_value=CSCFeatureData(
                    features=bitmask1,
                    wheel_revolution_data_supported=True,
                    crank_revolution_data_supported=True,
                    multiple_sensor_locations_supported=False,
                ),
                description="Wheel and Crank Revolution Data Supported (0x03)",
            ),
            CharacteristicTestData(
                input_data=bytearray(bitmask2.to_bytes(2, "little")),
                expected_value=CSCFeatureData(
                    features=bitmask2,
                    wheel_revolution_data_supported=True,
                    crank_revolution_data_supported=False,
                    multiple_sensor_locations_supported=True,
                ),
                description="Wheel Revolution and Multiple Locations Supported",
            ),
        ]
