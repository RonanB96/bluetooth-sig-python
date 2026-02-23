"""Tests for ChromaticDistanceFromPlanckian characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ChromaticDistanceFromPlanckianCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestChromaticDistanceFromPlanckianCharacteristic(CommonCharacteristicTests):
    """Test suite for ChromaticDistanceFromPlanckian characteristic."""

    @pytest.fixture
    def characteristic(self) -> ChromaticDistanceFromPlanckianCharacteristic:
        """Provide ChromaticDistanceFromPlanckian characteristic."""
        return ChromaticDistanceFromPlanckianCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for ChromaticDistanceFromPlanckian."""
        return "2AE3"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for ChromaticDistanceFromPlanckian."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=0.0,
                description="zero",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00]),
                expected_value=0.001,
                description="100 * 1e-5 = 0.001",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=1e-05,
                description="1 * 1e-5",
            ),
        ]
