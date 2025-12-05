"""Tests for Indoor Positioning Configuration characteristic (0x2AAD)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.indoor_positioning_configuration import (
    IndoorPositioningConfigurationCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestIndoorPositioningConfigurationCharacteristic(CommonCharacteristicTests):
    """Test suite for Indoor Positioning Configuration characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Tests configuration values for indoor positioning systems.
    """

    @pytest.fixture
    def characteristic(self) -> IndoorPositioningConfigurationCharacteristic:
        """Return an Indoor Positioning Configuration characteristic instance."""
        return IndoorPositioningConfigurationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Indoor Positioning Configuration characteristic."""
        return "2AAD"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for indoor positioning configuration values."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]), expected_value=0, description="Configuration value 0 (default/minimum)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x7F]), expected_value=127, description="Configuration value 127 (mid-range)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF]), expected_value=255, description="Configuration value 255 (maximum)"
            ),
        ]
