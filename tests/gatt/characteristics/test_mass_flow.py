"""Tests for MassFlow characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import MassFlowCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestMassFlowCharacteristic(CommonCharacteristicTests):
    """Test suite for MassFlow characteristic."""

    @pytest.fixture
    def characteristic(self) -> MassFlowCharacteristic:
        """Provide MassFlow characteristic."""
        return MassFlowCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for MassFlow."""
        return "2B02"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for MassFlow."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=0,
                description="zero flow",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03]),
                expected_value=1000,
                description="1000 g/s",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=1,
                description="1 g/s",
            ),
        ]
