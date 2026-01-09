"""Tests for Anaerobic Heart Rate Lower Limit characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import AnaerobicHeartRateLowerLimitCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAnaerobicHeartRateLowerLimitCharacteristic(CommonCharacteristicTests):
    """Test suite for Anaerobic Heart Rate Lower Limit characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds anaerobic heart rate lower limit-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> AnaerobicHeartRateLowerLimitCharacteristic:
        """Return an Anaerobic Heart Rate Lower Limit characteristic instance."""
        return AnaerobicHeartRateLowerLimitCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Anaerobic Heart Rate Lower Limit characteristic."""
        return "2A81"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for anaerobic heart rate lower limit."""
        return [
            CharacteristicTestData(input_data=bytearray([140]), expected_value=140, description="140 BPM"),
            CharacteristicTestData(input_data=bytearray([160]), expected_value=160, description="160 BPM"),
            CharacteristicTestData(input_data=bytearray([180]), expected_value=180, description="180 BPM"),
        ]

    # === Anaerobic Heart Rate Lower Limit-Specific Tests ===

    @pytest.mark.parametrize(
        "heart_rate",
        [
            140,  # 140 BPM
            150,  # 150 BPM
            160,  # 160 BPM
            170,  # 170 BPM
            180,  # 180 BPM
        ],
    )
    def test_anaerobic_heart_rate_lower_limit_values(
        self, characteristic: AnaerobicHeartRateLowerLimitCharacteristic, heart_rate: int
    ) -> None:
        """Test anaerobic heart rate lower limit with various valid values."""
        data = bytearray([heart_rate])
        result = characteristic.parse_value(data)
        assert result == heart_rate

    def test_anaerobic_heart_rate_lower_limit_boundary_values(
        self, characteristic: AnaerobicHeartRateLowerLimitCharacteristic
    ) -> None:
        """Test anaerobic heart rate lower limit boundary values."""
        # Test minimum value (0 BPM)
        result = characteristic.parse_value(bytearray([0]))
        assert result == 0

        # Test maximum value (255 BPM)
        result = characteristic.parse_value(bytearray([255]))
        assert result == 255
