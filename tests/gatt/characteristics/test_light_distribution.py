"""Tests for LightDistribution characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import LightDistributionCharacteristic
from bluetooth_sig.gatt.characteristics.light_distribution import LightDistributionType
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestLightDistributionCharacteristic(CommonCharacteristicTests):
    """Test suite for LightDistribution characteristic."""

    @pytest.fixture
    def characteristic(self) -> LightDistributionCharacteristic:
        """Provide LightDistribution characteristic."""
        return LightDistributionCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for LightDistribution."""
        return "2BE1"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for LightDistribution."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=LightDistributionType.NOT_SPECIFIED,
                description="not specified",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=LightDistributionType.TYPE_I,
                description="type I",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05]),
                expected_value=LightDistributionType.TYPE_V,
                description="type V",
            ),
        ]
