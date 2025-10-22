"""Test glucose measurement context characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import GlucoseMeasurementContextCharacteristic
from bluetooth_sig.gatt.characteristics.glucose_measurement_context import (
    CarbohydrateType,
    GlucoseMeasurementContextFlags,
    MealType,
)

from .test_characteristic_common import CommonCharacteristicTests


class TestGlucoseMeasurementContextCharacteristic(CommonCharacteristicTests):
    """Test Glucose Measurement Context characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> GlucoseMeasurementContextCharacteristic:
        """Fixture providing a glucose measurement context characteristic."""
        return GlucoseMeasurementContextCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for glucose measurement context characteristic."""
        return "2A34"

    @pytest.fixture
    def valid_test_data(self) -> tuple[bytearray, float]:
        """Valid test data for glucose measurement context characteristic."""
        # Create minimal test data: flags(1) + seq_num(2)
        test_data = bytearray(
            [
                0x00,  # flags: no optional fields
                0x2A,
                0x00,  # sequence number = 42
            ]
        )
        return test_data, 42.0

    def test_glucose_context_basic_parsing(self, characteristic: GlucoseMeasurementContextCharacteristic) -> None:
        """Test basic glucose context data parsing."""
        test_data, _ = self.valid_test_data()

        result = characteristic.decode_value(test_data)
        assert result.sequence_number == 42
        assert result.flags == GlucoseMeasurementContextFlags(0)

    def test_glucose_context_with_carbohydrate(self, characteristic: GlucoseMeasurementContextCharacteristic) -> None:
        """Test glucose context with carbohydrate data."""
        # Flags: 0x02 (carbohydrate present)
        test_data = bytearray(
            [
                0x02,  # flags: carbohydrate present
                0x01,
                0x00,  # sequence number = 1
                0x01,  # carbohydrate ID = 1 (Breakfast)
                0x40,
                0x1C,  # carbohydrate: 50.0g as SFLOAT
            ]
        )

        result = characteristic.decode_value(test_data)
        assert result.carbohydrate_id == CarbohydrateType.BREAKFAST
        # Human-readable name should match the enum's string representation
        assert str(result.carbohydrate_id) == "Breakfast"

    def test_glucose_context_with_meal(self, characteristic: GlucoseMeasurementContextCharacteristic) -> None:
        """Test glucose context with meal information."""
        # Flags: 0x04 (meal present)
        test_data = bytearray(
            [
                0x04,  # flags: meal present
                0x01,
                0x00,  # sequence number = 1
                0x02,  # meal = 2 (Postprandial)
            ]
        )

        result = characteristic.decode_value(test_data)
        assert result.meal == MealType.POSTPRANDIAL
        # Human-readable meal name should match the enum's string representation
        assert str(result.meal) == "Postprandial (after meal)"

    def test_glucose_context_invalid_data(self, characteristic: GlucoseMeasurementContextCharacteristic) -> None:
        """Test glucose context with invalid data."""
        with pytest.raises(ValueError, match="must be at least 3 bytes"):
            characteristic.decode_value(bytearray([0x00, 0x01]))
