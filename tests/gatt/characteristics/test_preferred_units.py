"""Tests for Preferred Units characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import PreferredUnitsCharacteristic, PreferredUnitsData
from bluetooth_sig.types.uuid import BluetoothUUID
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPreferredUnitsCharacteristic(CommonCharacteristicTests):
    """Test suite for Preferred Units characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds preferred units-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> PreferredUnitsCharacteristic:
        """Return a Preferred Units characteristic instance."""
        return PreferredUnitsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Preferred Units characteristic."""
        return "2B46"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for preferred units."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x27]),  # 0x2700 = unitless
                expected_value=PreferredUnitsData(units=[BluetoothUUID(0x2700)]),
                description="Unitless unit",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x27]),  # 0x2701 = length (metre)
                expected_value=PreferredUnitsData(units=[BluetoothUUID(0x2701)]),
                description="Length unit",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x27]),  # 0x2702 = mass (kilogram)
                expected_value=PreferredUnitsData(units=[BluetoothUUID(0x2702)]),
                description="Mass unit",
            ),
        ]

    # === Preferred Units-Specific Tests ===

    @pytest.mark.parametrize(
        "units_value",
        [
            0x2700,  # unitless
            0x2701,  # length (metre)
            0x2702,  # mass (kilogram)
        ],
    )
    def test_preferred_units_values(self, characteristic: PreferredUnitsCharacteristic, units_value: int) -> None:
        """Test preferred units with various valid unit UUIDs."""
        data = bytearray([units_value & 0xFF, (units_value >> 8) & 0xFF])
        result = characteristic.parse_value(data)
        expected = PreferredUnitsData(units=[BluetoothUUID(units_value)])
        assert result.value == expected

    def test_preferred_units_boundary_values(self, characteristic: PreferredUnitsCharacteristic) -> None:
        """Test preferred units boundary values using actual unit UUIDs."""
        # Test first unit UUID (0x2700 = unitless)
        result = characteristic.parse_value(bytearray([0x00, 0x27]))
        assert result.value == PreferredUnitsData(units=[BluetoothUUID(0x2700)])

        # Test last unit UUID (0x27C9 = Gravity)
        result = characteristic.parse_value(bytearray([0xC9, 0x27]))
        assert result.value == PreferredUnitsData(units=[BluetoothUUID(0x27C9)])

    def test_preferred_units_multiple_values(self, characteristic: PreferredUnitsCharacteristic) -> None:
        """Test preferred units with multiple unit values."""
        # Test with two actual unit UUIDs: 0x2700 (unitless), 0x2701 (length)
        data = bytearray([0x00, 0x27, 0x01, 0x27])
        result = characteristic.parse_value(data)
        expected = PreferredUnitsData(units=[BluetoothUUID(0x2700), BluetoothUUID(0x2701)])
        assert result.value == expected

    def test_preferred_units_encoding(self, characteristic: PreferredUnitsCharacteristic) -> None:
        """Test encoding preferred units back to bytes."""
        data = PreferredUnitsData(units=[BluetoothUUID(0x2700), BluetoothUUID(0x2701), BluetoothUUID(0x2702)])
        result = characteristic.build_value(data)
        expected = bytearray([0x00, 0x27, 0x01, 0x27, 0x02, 0x27])
        assert result == expected

    def test_get_unit_names_known_units(self, characteristic: PreferredUnitsCharacteristic) -> None:
        """Test getting unit information for known Bluetooth SIG units."""
        # Use actual unit UUIDs from the registry
        data = PreferredUnitsData(units=[BluetoothUUID(0x2700), BluetoothUUID(0x2701)])  # unitless, length (metre)
        units = characteristic.get_units(data)
        assert len(units) == 2
        assert "unitless" in units[0].name.lower()
        assert "length" in units[1].name.lower() or "metre" in units[1].name.lower()

    def test_get_unit_names_unknown_units(self, characteristic: PreferredUnitsCharacteristic) -> None:
        """Test getting unit information for unknown unit UUIDs."""
        data = PreferredUnitsData(units=[BluetoothUUID(0x2708), BluetoothUUID(0x0000)])  # Unknown units
        units = characteristic.get_units(data)
        assert len(units) == 2
        assert "Unknown Unit" in units[0].name
        assert "Unknown Unit" in units[1].name
        assert "2708" in units[0].name
        assert "0000" in units[1].name

    def test_validate_units_valid(self, characteristic: PreferredUnitsCharacteristic) -> None:
        """Test validation of valid unit UUIDs."""
        data = PreferredUnitsData(units=[BluetoothUUID(0x2700), BluetoothUUID(0x2701)])  # Known units
        errors = characteristic.validate_units(data)
        assert len(errors) == 0

    def test_validate_units_invalid(self, characteristic: PreferredUnitsCharacteristic) -> None:
        """Test validation of invalid unit UUIDs."""
        data = PreferredUnitsData(units=[BluetoothUUID(0x2708), BluetoothUUID(0x2700)])  # One invalid, one valid
        errors = characteristic.validate_units(data)
        assert len(errors) == 1
        assert "2708" in errors[0]
        assert "not a recognized" in errors[0]
