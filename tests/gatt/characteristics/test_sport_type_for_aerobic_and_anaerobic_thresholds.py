"""Tests for Sport Type for Aerobic and Anaerobic Thresholds characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import SportType, SportTypeForAerobicAndAnaerobicThresholdsCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSportTypeForAerobicAndAnaerobicThresholdsCharacteristic(CommonCharacteristicTests):
    """Test suite for Sport Type for Aerobic and Anaerobic Thresholds characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds sport type-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> SportTypeForAerobicAndAnaerobicThresholdsCharacteristic:
        """Return a Sport Type for Aerobic and Anaerobic Thresholds characteristic instance."""
        return SportTypeForAerobicAndAnaerobicThresholdsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Sport Type for Aerobic and Anaerobic Thresholds characteristic."""
        return "2A93"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for sport type."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0]), expected_value=SportType.UNSPECIFIED, description="Unspecified"
            ),
            CharacteristicTestData(
                input_data=bytearray([1]), expected_value=SportType.RUNNING_TREADMILL, description="Running"
            ),
            CharacteristicTestData(
                input_data=bytearray([2]), expected_value=SportType.CYCLING_ERGOMETER, description="Cycling"
            ),
        ]

    # === Sport Type-Specific Tests ===

    @pytest.mark.parametrize(
        "sport_type_value,expected_enum,description",
        [
            (0, SportType.UNSPECIFIED, "Unspecified"),
            (1, SportType.RUNNING_TREADMILL, "Running"),
            (2, SportType.CYCLING_ERGOMETER, "Cycling"),
            (3, SportType.ROWING_ERGOMETER, "Rowing"),
            (4, SportType.CROSS_TRAINING_ELLIPTICAL, "Cross training"),
        ],
    )
    def test_sport_type_values(
        self,
        characteristic: SportTypeForAerobicAndAnaerobicThresholdsCharacteristic,
        sport_type_value: int,
        expected_enum: SportType,
        description: str,
    ) -> None:
        """Test sport type with various valid values."""
        data = bytearray([sport_type_value])
        result = characteristic.parse_value(data)
        assert result.value == expected_enum

    def test_sport_type_boundary_values(
        self, characteristic: SportTypeForAerobicAndAnaerobicThresholdsCharacteristic
    ) -> None:
        """Test sport type boundary values."""
        # Test minimum value (0)
        result = characteristic.parse_value(bytearray([0]))
        assert result.value == SportType.UNSPECIFIED

        # Test maximum valid value (11)
        result = characteristic.parse_value(bytearray([11]))
        assert result.value == SportType.WHOLE_BODY_EXERCISING

    def test_sport_type_invalid_values(
        self, characteristic: SportTypeForAerobicAndAnaerobicThresholdsCharacteristic
    ) -> None:
        """Test sport type with invalid values."""
        # Test invalid value (12 is reserved) - parse_value returns parse_success=False
        result = characteristic.parse_value(bytearray([12]))
        assert result.parse_success is False
        assert "SportType" in (result.error_message or "")

    def test_sport_type_encoding(self, characteristic: SportTypeForAerobicAndAnaerobicThresholdsCharacteristic) -> None:
        """Test encoding sport type back to bytes."""
        data = SportType.RUNNING_TREADMILL
        result = characteristic.build_value(data)
        assert result == bytearray([1])
