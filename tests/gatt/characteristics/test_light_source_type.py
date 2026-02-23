"""Tests for LightSourceType characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import LightSourceTypeCharacteristic
from bluetooth_sig.gatt.characteristics.light_source_type import LightSourceTypeValue
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestLightSourceTypeCharacteristic(CommonCharacteristicTests):
    """Test suite for LightSourceType characteristic."""

    @pytest.fixture
    def characteristic(self) -> LightSourceTypeCharacteristic:
        """Provide LightSourceType characteristic."""
        return LightSourceTypeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for LightSourceType."""
        return "2BE3"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for LightSourceType."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=LightSourceTypeValue.NOT_SPECIFIED,
                description="not specified",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x04]),
                expected_value=LightSourceTypeValue.INCANDESCENT,
                description="incandescent",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05]),
                expected_value=LightSourceTypeValue.LED,
                description="LED",
            ),
        ]
