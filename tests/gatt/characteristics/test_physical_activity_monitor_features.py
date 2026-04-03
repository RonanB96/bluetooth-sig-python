"""Tests for PhysicalActivityMonitorFeaturesCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.physical_activity_monitor_features import (
    PhysicalActivityMonitorFeatures,
    PhysicalActivityMonitorFeaturesCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestPhysicalActivityMonitorFeaturesCharacteristic(CommonCharacteristicTests):
    """PhysicalActivityMonitorFeaturesCharacteristic test suite."""

    @pytest.fixture
    def characteristic(self) -> PhysicalActivityMonitorFeaturesCharacteristic:
        return PhysicalActivityMonitorFeaturesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B3B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=PhysicalActivityMonitorFeatures(0),
                description="No features supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=PhysicalActivityMonitorFeatures.MULTIPLE_USERS_SUPPORTED,
                description="Multiple users supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00]),
                expected_value=PhysicalActivityMonitorFeatures.HEART_RATE_SUPPORTED,
                description="Heart rate supported (bit 32)",
            ),
        ]
