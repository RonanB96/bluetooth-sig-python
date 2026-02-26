"""Tests for SulfurHexafluorideConcentration characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import SulfurHexafluorideConcentrationCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestSulfurHexafluorideConcentrationCharacteristic(CommonCharacteristicTests):
    """Test suite for SulfurHexafluorideConcentration characteristic."""

    @pytest.fixture
    def characteristic(self) -> SulfurHexafluorideConcentrationCharacteristic:
        """Provide SulfurHexafluorideConcentration characteristic."""
        return SulfurHexafluorideConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for SulfurHexafluorideConcentration."""
        return "2BD9"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for SulfurHexafluorideConcentration."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x80]),
                expected_value=100.0,
                description="100.0 ppm",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x80]),
                expected_value=1.0,
                description="1.0 ppm",
            ),
        ]
