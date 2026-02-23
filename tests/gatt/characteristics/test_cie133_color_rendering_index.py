"""Tests for CIE133ColorRenderingIndex characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import CIE133ColorRenderingIndexCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestCIE133ColorRenderingIndexCharacteristic(CommonCharacteristicTests):
    """Test suite for CIE133ColorRenderingIndex characteristic."""

    @pytest.fixture
    def characteristic(self) -> CIE133ColorRenderingIndexCharacteristic:
        """Provide CIE133ColorRenderingIndex characteristic."""
        return CIE133ColorRenderingIndexCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for CIE133ColorRenderingIndex."""
        return "2AE7"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for CIE133ColorRenderingIndex."""
        return [
            CharacteristicTestData(
                input_data=bytearray([50]),
                expected_value=50,
                description="CRI of 50",
            ),
            CharacteristicTestData(
                input_data=bytearray([100]),
                expected_value=100,
                description="CRI of 100",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x80]),
                expected_value=-128,
                description="minimum CRI",
            ),
        ]
