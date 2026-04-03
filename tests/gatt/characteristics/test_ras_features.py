"""Tests for RAS Features characteristic (0x2C14)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.ras_features import RASFeatures, RASFeaturesCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRASFeaturesCharacteristic(CommonCharacteristicTests):
    """Test suite for RAS Features characteristic."""

    @pytest.fixture
    def characteristic(self) -> RASFeaturesCharacteristic:
        return RASFeaturesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C14"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=RASFeatures(0),
                description="No features supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05, 0x00, 0x00, 0x00]),
                expected_value=(RASFeatures.REAL_TIME_RANGING_DATA_SUPPORTED | RASFeatures.ABORT_OPERATION_SUPPORTED),
                description="Real-time and abort features",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x08, 0x00, 0x00, 0x00]),
                expected_value=RASFeatures.FILTER_RANGING_DATA_SUPPORTED,
                description="Filter ranging data supported only",
            ),
        ]
