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
        """Provide Cycling Power Feature characteristic for testing."""
        return CyclingPowerFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Cycling Power Feature characteristic."""
        return "2A65"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid cycling power feature test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray(struct.pack("<I", 0x0000000F)),
                expected_value=CyclingPowerFeatureData(
                    features=(
                        CyclingPowerFeatures.PEDAL_POWER_BALANCE_SUPPORTED
                        | CyclingPowerFeatures.ACCUMULATED_ENERGY_SUPPORTED
                        | CyclingPowerFeatures.WHEEL_REVOLUTION_DATA_SUPPORTED
                        | CyclingPowerFeatures.CRANK_REVOLUTION_DATA_SUPPORTED
                    ),
                    pedal_power_balance_supported=True,
                    accumulated_energy_supported=True,
                    wheel_revolution_data_supported=True,
                    crank_revolution_data_supported=True,
                ),
                description="Multiple features enabled",
            ),
            CharacteristicTestData(
                input_data=bytearray(struct.pack("<I", 0x00000001)),
                expected_value=CyclingPowerFeatureData(
                    features=CyclingPowerFeatures.PEDAL_POWER_BALANCE_SUPPORTED,
                    pedal_power_balance_supported=True,
                    accumulated_energy_supported=False,
                    wheel_revolution_data_supported=False,
                    crank_revolution_data_supported=False,
                ),
                description="Only pedal power balance supported",
            ),
        ]

    def test_cycling_power_feature_values(self, characteristic: CyclingPowerFeatureCharacteristic) -> None:
        """Test parsing cycling power feature values."""
        # Test basic feature mask
        feature_data = struct.pack("<I", 0x0000000F)  # Multiple features enabled
        result = characteristic.parse_value(bytearray(feature_data))
        assert result.value is not None
        assert result.value.features == (
            CyclingPowerFeatures.PEDAL_POWER_BALANCE_SUPPORTED
            | CyclingPowerFeatures.ACCUMULATED_ENERGY_SUPPORTED
            | CyclingPowerFeatures.WHEEL_REVOLUTION_DATA_SUPPORTED
            | CyclingPowerFeatures.CRANK_REVOLUTION_DATA_SUPPORTED
        )
        assert result.value.pedal_power_balance_supported is True
        assert result.value.accumulated_energy_supported is True
        assert result.value.wheel_revolution_data_supported is True
        assert result.value.crank_revolution_data_supported is True

        # Test single feature
        feature_data = struct.pack("<I", 0x00000001)  # Only pedal power balance
        result = characteristic.parse_value(bytearray(feature_data))
        assert result.value is not None
        assert result.value.features == CyclingPowerFeatures.PEDAL_POWER_BALANCE_SUPPORTED
        assert result.value.pedal_power_balance_supported is True
        assert result.value.accumulated_energy_supported is False
        assert result.value.wheel_revolution_data_supported is False
        assert result.value.crank_revolution_data_supported is False

        # Test no features
        feature_data = struct.pack("<I", 0x00000000)
        result = characteristic.parse_value(bytearray(feature_data))
        assert result.value is not None
        assert result.value.features == CyclingPowerFeatures(0)
        assert result.value.pedal_power_balance_supported is False
        assert result.value.accumulated_energy_supported is False
        assert result.value.wheel_revolution_data_supported is False
        assert result.value.crank_revolution_data_supported is False
