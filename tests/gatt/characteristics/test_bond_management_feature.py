"""Tests for Bond Management Feature characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import BondManagementFeatureCharacteristic
from bluetooth_sig.gatt.characteristics.bond_management_feature import BondManagementFeatureFlags
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBondManagementFeatureCharacteristic(CommonCharacteristicTests):
    """Test suite for Bond Management Feature characteristic."""

    @pytest.fixture
    def characteristic(self) -> BondManagementFeatureCharacteristic:
        return BondManagementFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AA5"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=BondManagementFeatureFlags(0),
                description="No features supported (1 byte)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=BondManagementFeatureFlags.DELETE_REQUESTING_BR_EDR_LE,
                description="Delete requesting BR/EDR+LE supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x01]),
                expected_value=(
                    BondManagementFeatureFlags.DELETE_REQUESTING_BR_EDR_LE
                    | BondManagementFeatureFlags.DELETE_ALL_BR_EDR
                ),
                description="Flags spanning two octets",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x41, 0x00, 0x02]),
                expected_value=(
                    BondManagementFeatureFlags.DELETE_REQUESTING_BR_EDR_LE
                    | BondManagementFeatureFlags.DELETE_ALL_BR_EDR_LE
                    | BondManagementFeatureFlags.DELETE_ALL_EXCEPT_REQUESTING_LE_AUTH
                ),
                description="Three-flag combination across three octets",
            ),
        ]

    def test_variable_length_encoding(self, characteristic: BondManagementFeatureCharacteristic) -> None:
        """Test that encoding uses minimum bytes."""
        # Single byte flag
        data = characteristic.build_value(BondManagementFeatureFlags.DELETE_REQUESTING_BR_EDR_LE)
        assert len(data) == 1
        assert data == bytearray([0x01])

        # Needs 2 bytes
        data = characteristic.build_value(BondManagementFeatureFlags.DELETE_ALL_BR_EDR)
        assert len(data) == 2
        assert data == bytearray([0x00, 0x01])

        # Needs 3 bytes
        data = characteristic.build_value(BondManagementFeatureFlags.DELETE_ALL_EXCEPT_REQUESTING_LE)
        assert len(data) == 3
        assert data == bytearray([0x00, 0x00, 0x01])
