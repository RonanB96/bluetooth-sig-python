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
                input_data=bytearray([0x00, 0x00]),
                expected_value=RASFeatures(0),
                description="No features supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x15, 0x00]),
                expected_value=(
                    RASFeatures.REAL_TIME_RANGING_DATA_SUPPORTED
                    | RASFeatures.ABORT_OPERATION_SUPPORTED
                    | RASFeatures.RANGING_DATA_READY_SUPPORTED
                ),
                description="Real-time, abort, and data ready features",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x3F, 0x00]),
                expected_value=RASFeatures(0x3F),
                description="All features supported",
            ),
        ]

    def test_roundtrip(self, characteristic: RASFeaturesCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for flags in [RASFeatures(0), RASFeatures.FILTER_RANGING_DATA_SUPPORTED, RASFeatures(0x3F)]:
            encoded = characteristic.build_value(flags)
            decoded = characteristic.parse_value(encoded)
            assert decoded == flags
