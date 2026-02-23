"""Tests for Energy32 characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import Energy32Characteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestEnergy32Characteristic(CommonCharacteristicTests):
    """Test suite for Energy32 characteristic."""

    @pytest.fixture
    def characteristic(self) -> Energy32Characteristic:
        """Provide Energy32 characteristic."""
        return Energy32Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Energy32."""
        return "2BA8"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for Energy32."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03, 0x00, 0x00]),
                expected_value=1000,
                description="1000 kWh",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00, 0x00]),
                expected_value=1,
                description="1 kWh",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x40, 0x42, 0x0F, 0x00]),
                expected_value=1000000,
                description="1M kWh",
            ),
        ]
