"""RC Feature characteristic (0x2B1D).

Describes the supported features of the Reconnection Configuration server.

Structure: E2E-CRC (uint16) + RC Feature field (3+n octets).
The RC Feature field is a variable-length bit field with an extension
mechanism via bit 23.

References:
    Bluetooth SIG Reconnection Configuration Service v1.0.1, Section 3.1
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class RCFeatureFlags(IntFlag):
    """RC Feature bit definitions as per RCS v1.0.1 Table 3.3."""

    E2E_CRC_SUPPORTED = 0x000001
    ENABLE_DISCONNECT_SUPPORTED = 0x000002
    READY_FOR_DISCONNECT_SUPPORTED = 0x000004
    PROPOSE_RECONNECTION_TIMEOUT_SUPPORTED = 0x000008
    PROPOSE_CONNECTION_INTERVAL_SUPPORTED = 0x000010
    PROPOSE_PERIPHERAL_LATENCY_SUPPORTED = 0x000020
    PROPOSE_SUPERVISION_TIMEOUT_SUPPORTED = 0x000040
    PROPOSE_ADVERTISEMENT_INTERVAL_SUPPORTED = 0x000080
    PROPOSE_ADVERTISEMENT_COUNT_SUPPORTED = 0x000100
    PROPOSE_ADVERTISEMENT_REPETITION_TIME_SUPPORTED = 0x000200
    ADVERTISEMENT_CONFIGURATION_1_SUPPORTED = 0x000400
    ADVERTISEMENT_CONFIGURATION_2_SUPPORTED = 0x000800
    ADVERTISEMENT_CONFIGURATION_3_SUPPORTED = 0x001000
    ADVERTISEMENT_CONFIGURATION_4_SUPPORTED = 0x002000
    UPGRADE_TO_LESC_ONLY_SUPPORTED = 0x004000
    NEXT_PAIRING_OOB_SUPPORTED = 0x008000
    USE_OF_FILTER_ACCEPT_LIST_SUPPORTED = 0x010000
    LIMITED_ACCESS_SUPPORTED = 0x020000


class RCFeatureData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed RC Feature characteristic data.

    Attributes:
        e2e_crc: CRC-CCITT value (0xFFFF if E2E-safety not supported).
        features: Supported feature flags from the RC Feature field.

    """

    e2e_crc: int
    features: RCFeatureFlags


class RCFeatureCharacteristic(BaseCharacteristic[RCFeatureData]):
    """RC Feature characteristic (0x2B1D).

    org.bluetooth.characteristic.rc_feature

    Composite characteristic: E2E-CRC (uint16) followed by
    a variable-length RC Feature bit field (3+ octets).
    """

    _E2E_CRC_SIZE = 2
    _MIN_FEATURE_OCTETS = 3
    _DEFINED_BITS_MASK = 0x03FFFF
    _BYTE_MASK = 0xFF
    _BITS_PER_BYTE = 8

    min_length = _E2E_CRC_SIZE + _MIN_FEATURE_OCTETS
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> RCFeatureData:
        """Parse RC Feature data per RCS v1.0.1 Section 3.1."""
        e2e_crc = DataParser.parse_int16(data, 0, signed=False)

        # RC Feature field starts after E2E-CRC, variable length (3+n octets).
        # Read all remaining bytes as little-endian integer.
        feature_bytes = data[self._E2E_CRC_SIZE :]
        value = 0
        for i, byte in enumerate(feature_bytes):
            value |= byte << (self._BITS_PER_BYTE * i)
        features = RCFeatureFlags(value & self._DEFINED_BITS_MASK)

        return RCFeatureData(e2e_crc=e2e_crc, features=features)

    def _encode_value(self, data: RCFeatureData) -> bytearray:
        """Encode RC Feature data."""
        result = bytearray()
        result.extend(DataParser.encode_int16(data.e2e_crc, signed=False))

        value = int(data.features)
        num_octets = max(self._MIN_FEATURE_OCTETS, (value.bit_length() + 7) // self._BITS_PER_BYTE)
        for i in range(num_octets):
            result.append((value >> (self._BITS_PER_BYTE * i)) & self._BYTE_MASK)
        return result
