"""Tests for Aerobic Threshold characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import AerobicThresholdCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAerobicThresholdCharacteristic(CommonCharacteristicTests):
    """Test suite for Aerobic Threshold characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds aerobic threshold-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> AerobicThresholdCharacteristic:
        """Return an Aerobic Threshold characteristic instance."""
        return AerobicThresholdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Aerobic Threshold characteristic."""
        return "2A7F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for aerobic threshold."""
        return [
            CharacteristicTestData(input_data=bytearray([120]), expected_value=120, description="120 bpm"),
            CharacteristicTestData(input_data=bytearray([140]), expected_value=140, description="140 bpm"),
            CharacteristicTestData(input_data=bytearray([160]), expected_value=160, description="160 bpm"),
        ]

    # === Aerobic Threshold-Specific Tests ===

    @pytest.mark.parametrize(
        "thresh",
        [
            100,  # Low threshold
            130,  # Moderate threshold
            150,  # High threshold
            180,  # Very high threshold
        ],
    )
    def test_aerobic_thresh_values(self, characteristic: AerobicThresholdCharacteristic, thresh: int) -> None:
        """Test aerobic threshold with various valid values."""
        data = bytearray([thresh])
        result = characteristic.parse_value(data)
        assert result == thresh

    def test_aerobic_threshold_boundary_values(self, characteristic: AerobicThresholdCharacteristic) -> None:
        """Test aerobic threshold boundary values."""
        # Test minimum (0 bpm)
        result = characteristic.parse_value(bytearray([0]))
        assert result == 0

        # Test maximum (255 bpm)
        result = characteristic.parse_value(bytearray([255]))
        assert result == 255
