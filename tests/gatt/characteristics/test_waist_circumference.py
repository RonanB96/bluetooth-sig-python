"""Tests for Waist Circumference characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import WaistCircumferenceCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestWaistCircumferenceCharacteristic(CommonCharacteristicTests):
    """Test suite for Waist Circumference characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds waist circumference-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> WaistCircumferenceCharacteristic:
        """Return a Waist Circumference characteristic instance."""
        return WaistCircumferenceCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Waist Circumference characteristic."""
        return "2A97"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for waist circumference."""
        return [
            CharacteristicTestData(input_data=bytearray([0x4C, 0x1D]), expected_value=75.0, description="75.0 cm"),
            CharacteristicTestData(input_data=bytearray([0x28, 0x23]), expected_value=90.0, description="90.0 cm"),
            CharacteristicTestData(input_data=bytearray([0x04, 0x29]), expected_value=105.0, description="105.0 cm"),
        ]

    # === Waist Circumference-Specific Tests ===

    @pytest.mark.parametrize(
        "waist_cm",
        [
            60.0,  # Small waist
            80.0,  # Average waist
            100.0,  # Large waist
            120.0,  # Very large waist
        ],
    )
    def test_waist_circ_values(self, characteristic: WaistCircumferenceCharacteristic, waist_cm: float) -> None:
        """Test waist circumference with various valid values."""
        # Convert cm to scaled uint16 (waist / 0.01)
        scaled_value = int(waist_cm / 0.01)
        data = bytearray([scaled_value & 0xFF, (scaled_value >> 8) & 0xFF])
        result = characteristic.parse_value(data)
        assert result.value is not None
        assert abs(result.value - waist_cm) < 0.01  # Allow small floating point error

    def test_waist_circ_boundary_values(self, characteristic: WaistCircumferenceCharacteristic) -> None:
        """Test waist circumference boundary values."""
        # Test minimum (0 cm)
        result = characteristic.parse_value(bytearray([0, 0]))
        assert result.value == 0.0

        # Test maximum (655.35 cm)
        result = characteristic.parse_value(bytearray([0xFF, 0xFF]))
        assert result.value is not None
        assert abs(result.value - 655.35) < 0.01
