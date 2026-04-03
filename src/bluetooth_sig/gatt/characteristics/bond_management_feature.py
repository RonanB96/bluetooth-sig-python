"""Bond Management Feature characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class BondManagementFeatureFlags(IntFlag):
    """Bond Management Feature flags as per BMS v1.0.1 Table 3.5.

    Variable-length bit field across up to 3 octets (18 defined bits).
    """

    DELETE_REQUESTING_BR_EDR_LE = 0x000001
    DELETE_REQUESTING_BR_EDR_LE_AUTH = 0x000002
    DELETE_REQUESTING_BR_EDR = 0x000004
    DELETE_REQUESTING_BR_EDR_AUTH = 0x000008
    DELETE_REQUESTING_LE = 0x000010
    DELETE_REQUESTING_LE_AUTH = 0x000020
    DELETE_ALL_BR_EDR_LE = 0x000040
    DELETE_ALL_BR_EDR_LE_AUTH = 0x000080
    DELETE_ALL_BR_EDR = 0x000100
    DELETE_ALL_BR_EDR_AUTH = 0x000200
    DELETE_ALL_LE = 0x000400
    DELETE_ALL_LE_AUTH = 0x000800
    DELETE_ALL_EXCEPT_REQUESTING_BR_EDR_LE = 0x001000
    DELETE_ALL_EXCEPT_REQUESTING_BR_EDR_LE_AUTH = 0x002000
    DELETE_ALL_EXCEPT_REQUESTING_BR_EDR = 0x004000
    DELETE_ALL_EXCEPT_REQUESTING_BR_EDR_AUTH = 0x008000
    DELETE_ALL_EXCEPT_REQUESTING_LE = 0x010000
    DELETE_ALL_EXCEPT_REQUESTING_LE_AUTH = 0x020000


class BondManagementFeatureCharacteristic(BaseCharacteristic[BondManagementFeatureFlags]):
    """Bond Management Feature characteristic (0x2AA5).

    org.bluetooth.characteristic.bond_management_feature

    Variable-length bit field (1-3 octets) where each bit indicates
    a supported bond management operation per BMS v1.0.1 Table 3.5.
    Server sends only enough octets for the highest set bit.
    """

    _MAX_OCTETS = 3
    _BITS_PER_BYTE = 8
    _BYTE_MASK = 0xFF

    min_length = 1
    max_length = _MAX_OCTETS
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> BondManagementFeatureFlags:
        """Decode Bond Management Feature data from variable-length bytes."""
        value = 0
        for i, byte in enumerate(data[: self._MAX_OCTETS]):
            value |= byte << (self._BITS_PER_BYTE * i)
        return BondManagementFeatureFlags(value)

    def _encode_value(self, data: BondManagementFeatureFlags) -> bytearray:
        """Encode Bond Management Feature flags to minimum required bytes."""
        value = int(data)
        if value == 0:
            return bytearray(self.min_length)
        num_octets = (value.bit_length() + 7) // self._BITS_PER_BYTE
        result = bytearray(num_octets)
        for i in range(num_octets):
            result[i] = (value >> (self._BITS_PER_BYTE * i)) & self._BYTE_MASK
        return result
