"""Test cycling power feature characteristic parsing."""

from __future__ import annotations

import struct

import pytest

from bluetooth_sig.gatt.characteristics import CyclingPowerFeatureCharacteristic
from bluetooth_sig.gatt.characteristics.cycling_power_feature import CyclingPowerFeatureData, CyclingPowerFeatures
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCyclingPowerFeatureCharacteristic(CommonCharacteristicTests):
    """Test Cycling Power Feature characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> CyclingPowerFeatureCharacteristic:
        return CyclingPowerFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A65"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(struct.pack("<I", 0x00000000)),
                expected_value=CyclingPowerFeatureData(features=CyclingPowerFeatures(0)),
                description="No features",
            ),
            CharacteristicTestData(
                input_data=bytearray(struct.pack("<I", 0x00000001)),
                expected_value=CyclingPowerFeatureData(
                    features=CyclingPowerFeatures.PEDAL_POWER_BALANCE_SUPPORTED,
                ),
                description="Only pedal power balance supported",
            ),
            CharacteristicTestData(
                input_data=bytearray(struct.pack("<I", 0x0000000F)),
                expected_value=CyclingPowerFeatureData(
                    features=(
                        CyclingPowerFeatures.PEDAL_POWER_BALANCE_SUPPORTED
                        | CyclingPowerFeatures.ACCUMULATED_TORQUE_SUPPORTED
                        | CyclingPowerFeatures.WHEEL_REVOLUTION_DATA_SUPPORTED
                        | CyclingPowerFeatures.CRANK_REVOLUTION_DATA_SUPPORTED
                    ),
                ),
                description="First 4 features enabled",
            ),
        ]

    def test_cycling_power_feature_values(self, characteristic: CyclingPowerFeatureCharacteristic) -> None:
        """Test parsing cycling power feature values."""
        # Test basic feature mask
        feature_data = struct.pack("<I", 0x0000000F)
        result = characteristic.parse_value(bytearray(feature_data))
        assert result is not None
        assert CyclingPowerFeatures.PEDAL_POWER_BALANCE_SUPPORTED in result.features
        assert CyclingPowerFeatures.ACCUMULATED_TORQUE_SUPPORTED in result.features
        assert CyclingPowerFeatures.WHEEL_REVOLUTION_DATA_SUPPORTED in result.features
        assert CyclingPowerFeatures.CRANK_REVOLUTION_DATA_SUPPORTED in result.features

        # Test single feature
        feature_data = struct.pack("<I", 0x00000001)
        result = characteristic.parse_value(bytearray(feature_data))
        assert CyclingPowerFeatures.PEDAL_POWER_BALANCE_SUPPORTED in result.features
        assert CyclingPowerFeatures.ACCUMULATED_TORQUE_SUPPORTED not in result.features

        # Test no features
        feature_data = struct.pack("<I", 0x00000000)
        result = characteristic.parse_value(bytearray(feature_data))
        assert result.features == CyclingPowerFeatures(0)

    def test_higher_bits(self, characteristic: CyclingPowerFeatureCharacteristic) -> None:
        """Test higher feature bits (CPS v1.1 bits 8-21)."""
        feature_data = struct.pack("<I", 0x00000100)  # OFFSET_COMPENSATION_INDICATOR_SUPPORTED
        result = characteristic.parse_value(bytearray(feature_data))
        assert CyclingPowerFeatures.OFFSET_COMPENSATION_INDICATOR_SUPPORTED in result.features

        feature_data = struct.pack("<I", 0x00080000)  # ENHANCED_OFFSET_COMPENSATION_SUPPORTED
        result = characteristic.parse_value(bytearray(feature_data))
        assert CyclingPowerFeatures.ENHANCED_OFFSET_COMPENSATION_SUPPORTED in result.features
