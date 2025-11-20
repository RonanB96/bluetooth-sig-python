"""Tests for Bond Management Feature characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import BondManagementFeatureCharacteristic
from bluetooth_sig.gatt.characteristics.bond_management_feature import BondManagementFeatureData
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBondManagementFeatureCharacteristic(CommonCharacteristicTests):
    """Test suite for Bond Management Feature characteristic."""

    @pytest.fixture
    def characteristic(self) -> BondManagementFeatureCharacteristic:
        """Return a Bond Management Feature characteristic instance."""
        return BondManagementFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Bond Management Feature characteristic."""
        return "2AA5"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for bond management feature."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0, 0, 0]),
                expected_value=BondManagementFeatureData(
                    delete_bond_of_requesting_device_supported=False,
                    delete_all_bonds_on_server_supported=False,
                    delete_all_but_active_bond_on_server_supported=False,
                ),
                description="No features supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([1, 0, 0]),
                expected_value=BondManagementFeatureData(
                    delete_bond_of_requesting_device_supported=True,
                    delete_all_bonds_on_server_supported=False,
                    delete_all_but_active_bond_on_server_supported=False,
                ),
                description="Delete bond of requesting device supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0, 1, 0]),
                expected_value=BondManagementFeatureData(
                    delete_bond_of_requesting_device_supported=False,
                    delete_all_bonds_on_server_supported=True,
                    delete_all_but_active_bond_on_server_supported=False,
                ),
                description="Delete all bonds on server supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0, 0, 1]),
                expected_value=BondManagementFeatureData(
                    delete_bond_of_requesting_device_supported=False,
                    delete_all_bonds_on_server_supported=False,
                    delete_all_but_active_bond_on_server_supported=True,
                ),
                description="Delete all but active bond on server supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([1, 1, 1]),
                expected_value=BondManagementFeatureData(
                    delete_bond_of_requesting_device_supported=True,
                    delete_all_bonds_on_server_supported=True,
                    delete_all_but_active_bond_on_server_supported=True,
                ),
                description="All features supported",
            ),
        ]

    def test_feature_flags_parsing(self, characteristic: BondManagementFeatureCharacteristic) -> None:
        """Test parsing of feature flags."""
        data = bytearray([1, 1, 0])  # First two features supported
        result = characteristic.decode_value(data)
        assert result.delete_bond_of_requesting_device_supported is True
        assert result.delete_all_bonds_on_server_supported is True
        assert result.delete_all_but_active_bond_on_server_supported is False

    def test_insufficient_data(self, characteristic: BondManagementFeatureCharacteristic) -> None:
        """Test that insufficient data raises ValueError."""
        with pytest.raises(ValueError, match="expected 3 bytes"):
            characteristic.decode_value(bytearray([1, 1]))  # Only 2 bytes
