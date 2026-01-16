"""HID Information characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

# Constants per Bluetooth HID specification
BCD_HID_MAX = 0xFFFF  # uint16 max for BCD HID version
COUNTRY_CODE_MAX = 0xFF  # uint8 max for country code
HID_INFO_DATA_LENGTH = 4  # Fixed data length: bcdHID(2) + bCountryCode(1) + Flags(1)


class HidInformationFlags(IntFlag):
    """HID Information flags as per Bluetooth HID specification."""

    REMOTE_WAKE = 0x01  # Bit 0: RemoteWake
    NORMALLY_CONNECTABLE = 0x02  # Bit 1: NormallyConnectable
    # Bits 2-7: Reserved


class HidInformationData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from HID Information characteristic.

    Attributes:
        bcd_hid: HID version in BCD format (uint16)
        b_country_code: Country code (uint8)
        flags: HID information flags
    """

    bcd_hid: int  # uint16
    b_country_code: int  # uint8
    flags: HidInformationFlags

    def __post_init__(self) -> None:
        """Validate HID information data."""
        if not 0 <= self.bcd_hid <= BCD_HID_MAX:
            raise ValueError(f"bcdHID must be 0-{BCD_HID_MAX:#x}, got {self.bcd_hid}")
        if not 0 <= self.b_country_code <= COUNTRY_CODE_MAX:
            raise ValueError(f"bCountryCode must be 0-{COUNTRY_CODE_MAX:#x}, got {self.b_country_code}")


class HidInformationCharacteristic(BaseCharacteristic[HidInformationData]):
    """HID Information characteristic (0x2A4A).

    org.bluetooth.characteristic.hid_information

    HID Information characteristic.
    """

    expected_length: int = 4  # bcdHID(2) + bCountryCode(1) + Flags(1)

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> HidInformationData:
        """Parse HID information data.

        Format: bcdHID(2) + bCountryCode(1) + Flags(1)

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context.

        Returns:
            HidInformationData containing parsed HID information.
        """
        if len(data) != HID_INFO_DATA_LENGTH:
            raise ValueError(f"HID Information data must be exactly {HID_INFO_DATA_LENGTH} bytes, got {len(data)}")

        bcd_hid = DataParser.parse_int16(data, 0, signed=False)
        b_country_code = DataParser.parse_int8(data, 2, signed=False)
        flags_value = DataParser.parse_int8(data, 3, signed=False)
        flags = HidInformationFlags(flags_value)

        return HidInformationData(
            bcd_hid=bcd_hid,
            b_country_code=b_country_code,
            flags=flags,
        )

    def _encode_value(self, data: HidInformationData) -> bytearray:
        """Encode HidInformationData back to bytes.

        Args:
            data: HidInformationData instance to encode

        Returns:
            Encoded bytes
        """
        result = bytearray()
        result.extend(DataParser.encode_int16(data.bcd_hid, signed=False))
        result.extend(DataParser.encode_int8(data.b_country_code, signed=False))
        result.extend(DataParser.encode_int8(int(data.flags), signed=False))
        return result
