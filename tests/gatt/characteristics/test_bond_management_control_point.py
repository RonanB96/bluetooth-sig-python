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
        return BondManagementControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AA4"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=BondManagementCommand.DELETE_BOND_OF_REQUESTING_DEVICE_BR_EDR_LE,
                description="Delete requesting device bond (BR/EDR+LE)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x04]),
                expected_value=BondManagementCommand.DELETE_ALL_BONDS_ON_SERVER_BR_EDR_LE,
                description="Delete all bonds (BR/EDR+LE)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x07]),
                expected_value=BondManagementCommand.DELETE_ALL_BUT_ACTIVE_BOND_ON_SERVER_BR_EDR_LE,
                description="Delete all but active bond (BR/EDR+LE)",
            ),
        ]

    def test_all_opcodes(self, characteristic: BondManagementControlPointCharacteristic) -> None:
        """Test parsing of all 9 defined opcodes."""
        for cmd in BondManagementCommand:
            result = characteristic.parse_value(bytearray([int(cmd)]))
            assert result == cmd

    def test_encode_commands(self, characteristic: BondManagementControlPointCharacteristic) -> None:
        """Test encoding of control commands."""
        data = characteristic.build_value(BondManagementCommand.DELETE_BOND_OF_REQUESTING_DEVICE_LE)
        assert data == bytearray([0x03])

        data = characteristic.build_value(BondManagementCommand.DELETE_ALL_BONDS_ON_SERVER_LE)
        assert data == bytearray([0x06])

    def test_insufficient_data(self, characteristic: BondManagementControlPointCharacteristic) -> None:
        """Test that empty data raises CharacteristicParseError."""
        from bluetooth_sig.gatt.exceptions import CharacteristicParseError

        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray())
