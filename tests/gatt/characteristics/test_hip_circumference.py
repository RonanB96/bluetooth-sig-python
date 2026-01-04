"""Tests for Hip Circumference characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import HipCircumferenceCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHipCircumferenceCharacteristic(CommonCharacteristicTests):
    """Test suite for Hip Circumference characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds hip circumference-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> HipCircumferenceCharacteristic:
        """Return a Hip Circumference characteristic instance."""
        return HipCircumferenceCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Hip Circumference characteristic."""
        return "2A8F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for hip circumference."""
        return [
            CharacteristicTestData(input_data=bytearray([0x34, 0x21]), expected_value=85.0, description="85.0 cm"),
            CharacteristicTestData(input_data=bytearray([0x1C, 0x25]), expected_value=95.0, description="95.0 cm"),
            CharacteristicTestData(input_data=bytearray([0xF8, 0x2A]), expected_value=110.0, description="110.0 cm"),
        ]

    # === Hip Circumference-Specific Tests ===

    @pytest.mark.parametrize(
        "hip_cm",
        [
            70.0,  # Small hips
            90.0,  # Average hips
            110.0,  # Large hips
            130.0,  # Very large hips
        ],
    )
    def test_hip_circ_values(self, characteristic: HipCircumferenceCharacteristic, hip_cm: float) -> None:
        """Test hip circumference with various valid values."""
        # Convert cm to scaled uint16 (hip / 0.01)
        scaled_value = int(hip_cm / 0.01)
        data = bytearray([scaled_value & 0xFF, (scaled_value >> 8) & 0xFF])
        result = characteristic.parse_value(data)
        assert abs(result - hip_cm) < 0.01  # Allow small floating point error

    def test_hip_circ_boundary_values(self, characteristic: HipCircumferenceCharacteristic) -> None:
        """Test hip circumference boundary values."""
        # Test minimum (0 cm)
        result = characteristic.parse_value(bytearray([0, 0]))
        assert result == 0.0

        # Test maximum (655.35 cm)
        result = characteristic.parse_value(bytearray([0xFF, 0xFF]))
        assert abs(result - 655.35) < 0.01
