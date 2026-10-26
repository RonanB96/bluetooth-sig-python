"""RC Settings characteristic (0x2B1E).

Structure per RCS v1.0.1, Section 3.2 (Table 3.4):
    Length (uint8, 1 octet) + Settings (2 octets) + [E2E-CRC (uint16, 0 or 2 octets)].

Settings bitfield (Table 3.5):
    Byte 0, bit 1: LESC Only
    Byte 0, bit 2: Use OOB Pairing
    Byte 0, bit 4: Ready for Disconnect
    Byte 0, bit 5: Limited Access
    Byte 0, bit 6: Access Permitted
    Byte 1, bits 0-1: Advertisement Mode (2-bit field)

References:
    Bluetooth SIG Reconnection Configuration Service v1.0.1, Section 3.2
"""

from __future__ import annotations

from enum import IntEnum, IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class RCSettingsFlags(IntFlag):
    """RC Settings bitfield flags (RCS v1.0.1 Table 3.5)."""

    LESC_ONLY = 0x0002
    USE_OOB_PAIRING = 0x0004
    READY_FOR_DISCONNECT = 0x0010
    LIMITED_ACCESS = 0x0020
    ACCESS_PERMITTED = 0x0040


class AdvertisementMode(IntEnum):
    """Advertisement mode (RCS v1.0.1 Table 3.5, byte 1 bits 0-1)."""

    ADV_IND = 0x00
    ADV_SCAN_IND = 0x01
    ADV_NONCONN_IND = 0x02
    ADV_DIRECT_IND = 0x03


class RCSettingsData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed RC Settings characteristic data.

    Attributes:
        length: Length field (uint8).
        settings_flags: Settings bitfield flags.
        advertisement_mode: Advertisement mode from byte 1 bits 0-1.
        e2e_crc: E2E-CRC value (None if not present).

    """

    length: int
    settings_flags: RCSettingsFlags
    advertisement_mode: AdvertisementMode
    e2e_crc: int | None = None


_ADV_MODE_SHIFT = 8
_ADV_MODE_MASK = 0x03
_FLAGS_MASK = 0x0076
_MIN_LENGTH_WITH_CRC = 5  # 1 (length) + 2 (settings) + 2 (CRC)


class RCSettingsCharacteristic(BaseCharacteristic[RCSettingsData]):
    """RC Settings characteristic (0x2B1E).

    org.bluetooth.characteristic.rc_settings

    Structure: Length(1) + Settings(2) + optional E2E-CRC(2).
    """

    min_length = 3
    max_length = 5
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> RCSettingsData:
        """Parse RC Settings data per RCS v1.0.1 Section 3.2."""
        length = DataParser.parse_int8(data, 0, signed=False)
        settings_raw = DataParser.parse_int16(data, 1, signed=False)

        settings_flags = RCSettingsFlags(settings_raw & _FLAGS_MASK)
        advertisement_mode = AdvertisementMode((settings_raw >> _ADV_MODE_SHIFT) & _ADV_MODE_MASK)

        e2e_crc: int | None = None
        if len(data) >= _MIN_LENGTH_WITH_CRC:
            e2e_crc = DataParser.parse_int16(data, 3, signed=False)

        return RCSettingsData(
            length=length,
            settings_flags=settings_flags,
            advertisement_mode=advertisement_mode,
            e2e_crc=e2e_crc,
        )

    def _encode_value(self, data: RCSettingsData) -> bytearray:
        """Encode RC Settings data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(data.length, signed=False))

        settings_raw = int(data.settings_flags) | (int(data.advertisement_mode) << _ADV_MODE_SHIFT)
        result.extend(DataParser.encode_int16(settings_raw, signed=False))

        if data.e2e_crc is not None:
            result.extend(DataParser.encode_int16(data.e2e_crc, signed=False))

        return result
