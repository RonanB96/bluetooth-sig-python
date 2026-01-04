"""Tests for Bond Management Control Point characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import BondManagementControlPointCharacteristic
from bluetooth_sig.gatt.characteristics.bond_management_control_point import BondManagementCommand
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBondManagementControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for Bond Management Control Point characteristic."""

    @pytest.fixture
    def characteristic(self) -> BondManagementControlPointCharacteristic:
        """Return a Bond Management Control Point characteristic instance."""
        return BondManagementControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Bond Management Control Point characteristic."""
        return "2AA4"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for bond management control point."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=BondManagementCommand.DELETE_BOND_OF_REQUESTING_DEVICE,
                description="Delete bond of requesting device",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02]),
                expected_value=BondManagementCommand.DELETE_ALL_BONDS_ON_SERVER,
                description="Delete all bonds on server",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03]),
                expected_value=BondManagementCommand.DELETE_ALL_BUT_ACTIVE_BOND_ON_SERVER,
                description="Delete all but active bond on server",
            ),
        ]

    def test_command_parsing(self, characteristic: BondManagementControlPointCharacteristic) -> None:
        """Test parsing of control commands."""
        # Test delete bond command
        result = characteristic.parse_value(bytearray([0x01]))
        assert result == BondManagementCommand.DELETE_BOND_OF_REQUESTING_DEVICE

        # Test delete all bonds command
        result = characteristic.parse_value(bytearray([0x02]))
        assert result == BondManagementCommand.DELETE_ALL_BONDS_ON_SERVER

        # Test delete all but active command
        result = characteristic.parse_value(bytearray([0x03]))
        assert result == BondManagementCommand.DELETE_ALL_BUT_ACTIVE_BOND_ON_SERVER

    def test_invalid_command(self, characteristic: BondManagementControlPointCharacteristic) -> None:
        """Test that invalid commands result in parse failure."""
        # parse_value returns parse_success=False for invalid commands
        result = characteristic.parse_value(bytearray([0x04]))  # Invalid command
        assert result.parse_success is False
        assert result.error_message == "Invalid BondManagementCommand: 4 (expected range [1, 3])"

    def test_insufficient_data(self, characteristic: BondManagementControlPointCharacteristic) -> None:
        """Test that insufficient data results in parse failure."""
        # parse_value returns parse_success=False for insufficient data
        result = characteristic.parse_value(bytearray())  # Empty data
        assert result.parse_success is False
        assert result.error_message == (
            "Length validation failed for Bond Management Control Point: expected at least 1 bytes, got 0 "
            "(class-level constraint for BondManagementControlPointCharacteristic)"
        )

    def test_encode_commands(self, characteristic: BondManagementControlPointCharacteristic) -> None:
        """Test encoding of control commands."""
        # Test encoding delete bond command
        data = characteristic.build_value(BondManagementCommand.DELETE_BOND_OF_REQUESTING_DEVICE)
        assert data == bytearray([0x01])

        # Test encoding delete all bonds command
        data = characteristic.build_value(BondManagementCommand.DELETE_ALL_BONDS_ON_SERVER)
        assert data == bytearray([0x02])

        # Test encoding delete all but active command
        data = characteristic.build_value(BondManagementCommand.DELETE_ALL_BUT_ACTIVE_BOND_ON_SERVER)
        assert data == bytearray([0x03])
