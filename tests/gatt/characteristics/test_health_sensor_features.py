"""Tests for HealthSensorFeaturesCharacteristic (2BF3)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.health_sensor_features import (
    HealthSensorFeatures,
    HealthSensorFeaturesCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHealthSensorFeatures(CommonCharacteristicTests):
    """Test suite for HealthSensorFeaturesCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> HealthSensorFeaturesCharacteristic:
        return HealthSensorFeaturesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BF3"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00, 0x00, 0x00, 0x00]), HealthSensorFeatures(0), "No features"),
            CharacteristicTestData(
                bytearray([0x01, 0x00, 0x00, 0x00]), HealthSensorFeatures.OBSERVATION_TYPE_SUPPORTED, "Observation type"
            ),
        ]
