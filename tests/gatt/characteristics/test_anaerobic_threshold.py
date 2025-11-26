"""Tests for Anaerobic Threshold characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import AnaerobicThresholdCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAnaerobicThresholdCharacteristic(CommonCharacteristicTests):
    """Test suite for Anaerobic Threshold characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds anaerobic threshold-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> AnaerobicThresholdCharacteristic:
        """Return an Anaerobic Threshold characteristic instance."""
        return AnaerobicThresholdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Anaerobic Threshold characteristic."""
        return "2A83"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for anaerobic threshold."""
        return [
            CharacteristicTestData(input_data=bytearray([150]), expected_value=150, description="150 bpm"),
            CharacteristicTestData(input_data=bytearray([170]), expected_value=170, description="170 bpm"),
            CharacteristicTestData(input_data=bytearray([190]), expected_value=190, description="190 bpm"),
        ]

    # === Anaerobic Threshold-Specific Tests ===

    @pytest.mark.parametrize(
        "thresh",
        [
            140,  # Low threshold
            160,  # Moderate threshold
            180,  # High threshold
            200,  # Very high threshold
        ],
    )
    def test_anaerobic_thresh_values(self, characteristic: AnaerobicThresholdCharacteristic, thresh: int) -> None:
        """Test anaerobic threshold with various valid values."""
        data = bytearray([thresh])
        result = characteristic.decode_value(data)
        assert result == thresh

    def test_anaerobic_thresh_boundary_values(self, characteristic: AnaerobicThresholdCharacteristic) -> None:
        """Test anaerobic threshold boundary values."""
        # Test minimum (0 bpm)
        result = characteristic.decode_value(bytearray([0]))
        assert result == 0

        # Test maximum (255 bpm)
        result = characteristic.decode_value(bytearray([255]))
        assert result == 255
