"""Tests for ChromaticityTolerance characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ChromaticityToleranceCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestChromaticityToleranceCharacteristic(CommonCharacteristicTests):
    """Test suite for ChromaticityTolerance characteristic."""

    @pytest.fixture
    def characteristic(self) -> ChromaticityToleranceCharacteristic:
        """Provide ChromaticityTolerance characteristic."""
        return ChromaticityToleranceCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for ChromaticityTolerance."""
        return "2AE6"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for ChromaticityTolerance."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0]),
                expected_value=0.0,
                description="zero tolerance",
            ),
            CharacteristicTestData(
                input_data=bytearray([100]),
                expected_value=0.01,
                description="100 * 1e-4 = 0.01",
            ),
            CharacteristicTestData(
                input_data=bytearray([200]),
                expected_value=0.02,
                description="200 * 1e-4 = 0.02",
            ),
            CharacteristicTestData(
                input_data=bytearray([254]),
                expected_value=0.0254,
                description="254 * 1e-4 = 0.0254",
            ),
        ]
