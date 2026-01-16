"""Bond Management Feature characteristic implementation."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class BondManagementFeatureData(msgspec.Struct, frozen=True, kw_only=True):
    """Bond Management Feature characteristic data structure."""

    delete_bond_of_requesting_device_supported: bool
    delete_all_bonds_on_server_supported: bool
    delete_all_but_active_bond_on_server_supported: bool


class BondManagementFeatureCharacteristic(BaseCharacteristic[BondManagementFeatureData]):
    """Bond Management Feature characteristic (0x2AA5).

    org.bluetooth.characteristic.bond_management_feature

    Read-only characteristic containing feature flags for bond management operations.
    3 bytes containing boolean flags for supported operations.
    """

    # SIG spec: three uint8 feature flags → fixed 3-byte payload; no GSS YAML
    expected_length = 3
    min_length = 3
    max_length = 3

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> BondManagementFeatureData:
        """Decode Bond Management Feature data from bytes.

        Args:
            data: Raw characteristic data (3 bytes)
            ctx: Optional characteristic context

        Returns:
            BondManagementFeatureData with feature flags

        Raises:
            ValueError: If data is insufficient

        """
        if len(data) < 3:
            raise ValueError(f"Insufficient data for Bond Management Feature: expected 3 bytes, got {len(data)}")

        # Parse feature flags (1 byte each)
        delete_bond_supported = bool(DataParser.parse_int8(data, 0, signed=False))
        delete_all_bonds_supported = bool(DataParser.parse_int8(data, 1, signed=False))
        delete_all_but_active_supported = bool(DataParser.parse_int8(data, 2, signed=False))

        return BondManagementFeatureData(
            delete_bond_of_requesting_device_supported=delete_bond_supported,
            delete_all_bonds_on_server_supported=delete_all_bonds_supported,
            delete_all_but_active_bond_on_server_supported=delete_all_but_active_supported,
        )

    def _encode_value(self, data: BondManagementFeatureData) -> bytearray:
        """Encode Bond Management Feature data to bytes.

        Args:
            data: BondManagementFeatureData to encode

        Returns:
            Encoded feature flags (3 bytes)

        """
        result = bytearray()

        # Encode feature flags (1 byte each)
        result.append(1 if data.delete_bond_of_requesting_device_supported else 0)
        result.append(1 if data.delete_all_bonds_on_server_supported else 0)
        result.append(1 if data.delete_all_but_active_bond_on_server_supported else 0)

        return result
