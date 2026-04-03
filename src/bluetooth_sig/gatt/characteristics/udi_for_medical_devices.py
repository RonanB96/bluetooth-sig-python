"""UDI for Medical Devices characteristic (0x2BFF).

Unique Device Identifier for medical devices per regional authority
(e.g. US FDA). Contains label, device identifier, issuer OID, and authority OID.

References:
    Bluetooth SIG GATT Specification Supplement
    org.bluetooth.characteristic.udi_for_medical_devices (GSS YAML)
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class UDIFlags(IntFlag):
    """UDI for Medical Devices flags."""

    UDI_LABEL_PRESENT = 0x01
    UDI_DEVICE_IDENTIFIER_PRESENT = 0x02
    UDI_ISSUER_PRESENT = 0x04
    UDI_AUTHORITY_PRESENT = 0x08


class UDIForMedicalDevicesData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from UDI for Medical Devices characteristic.

    Attributes:
        flags: Presence flags for optional fields.
        udi_label: The full UDI in human-readable form. None if absent.
        device_identifier: The DI portion of the UDI. None if absent.
        udi_issuer: OID of the UDI issuing organisation. None if absent.
        udi_authority: OID of the regional UDI authority. None if absent.

    """

    flags: UDIFlags
    udi_label: str | None = None
    device_identifier: str | None = None
    udi_issuer: str | None = None
    udi_authority: str | None = None


def _read_null_terminated_string(data: bytearray, offset: int) -> tuple[str, int]:
    """Read a null-terminated UTF-8 string from data at offset.

    Returns:
        Tuple of (string, new_offset past the null terminator).

    """
    end = data.index(0x00, offset) if 0x00 in data[offset:] else len(data)
    s = data[offset:end].decode("utf-8", errors="replace")
    return s, end + 1  # skip past null terminator


class UDIForMedicalDevicesCharacteristic(BaseCharacteristic[UDIForMedicalDevicesData]):
    """UDI for Medical Devices characteristic (0x2BFF).

    org.bluetooth.characteristic.udi_for_medical_devices

    Contains the Unique Device Identifier assigned to a medical device.
    """

    min_length = 1  # At minimum, flags byte
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> UDIForMedicalDevicesData:
        """Parse UDI for Medical Devices data.

        Format: Flags (uint8) + [UDI Label (utf8s, null-terminated)] +
                [Device Identifier (utf8s, null-terminated)] +
                [UDI Issuer (utf8s, null-terminated)] +
                [UDI Authority (utf8s, null-terminated)]
        """
        flags = UDIFlags(DataParser.parse_int8(data, 0, signed=False))
        offset = 1

        udi_label: str | None = None
        device_identifier: str | None = None
        udi_issuer: str | None = None
        udi_authority: str | None = None

        if flags & UDIFlags.UDI_LABEL_PRESENT and offset < len(data):
            udi_label, offset = _read_null_terminated_string(data, offset)

        if flags & UDIFlags.UDI_DEVICE_IDENTIFIER_PRESENT and offset < len(data):
            device_identifier, offset = _read_null_terminated_string(data, offset)

        if flags & UDIFlags.UDI_ISSUER_PRESENT and offset < len(data):
            udi_issuer, offset = _read_null_terminated_string(data, offset)

        if flags & UDIFlags.UDI_AUTHORITY_PRESENT and offset < len(data):
            udi_authority, offset = _read_null_terminated_string(data, offset)

        return UDIForMedicalDevicesData(
            flags=flags,
            udi_label=udi_label,
            device_identifier=device_identifier,
            udi_issuer=udi_issuer,
            udi_authority=udi_authority,
        )

    def _encode_value(self, data: UDIForMedicalDevicesData) -> bytearray:
        """Encode UDI for Medical Devices data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.flags), signed=False))

        if data.udi_label is not None:
            result.extend(data.udi_label.encode("utf-8"))
            result.append(0x00)

        if data.device_identifier is not None:
            result.extend(data.device_identifier.encode("utf-8"))
            result.append(0x00)

        if data.udi_issuer is not None:
            result.extend(data.udi_issuer.encode("utf-8"))
            result.append(0x00)

        if data.udi_authority is not None:
            result.extend(data.udi_authority.encode("utf-8"))
            result.append(0x00)

        return result
