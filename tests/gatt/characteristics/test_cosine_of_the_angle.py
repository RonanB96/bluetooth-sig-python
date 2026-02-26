"""Tests for CosineOfTheAngle characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import CosineOfTheAngleCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestCosineOfTheAngleCharacteristic(CommonCharacteristicTests):
    """Test suite for CosineOfTheAngle characteristic."""

    @pytest.fixture
    def characteristic(self) -> CosineOfTheAngleCharacteristic:
        """Provide CosineOfTheAngle characteristic."""
        return CosineOfTheAngleCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for CosineOfTheAngle."""
        return "2B8D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for CosineOfTheAngle."""
        return [
            CharacteristicTestData(
                input_data=bytearray([100]),
                expected_value=1.0,
                description="100 * 0.01 = 1.0",
            ),
            CharacteristicTestData(
                input_data=bytearray([50]),
                expected_value=0.5,
                description="50 * 0.01 = 0.5",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x9C]),
                expected_value=-1.0,
                description="-100 * 0.01 = -1.0",
            ),
        ]
