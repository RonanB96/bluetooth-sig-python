"""IEEE 11073-20601 Regulatory Certification Data List characteristic.

Implements the IEEE 11073-20601 Regulatory Certification Data List
characteristic (0x2A2A).

Structure (from GSS YAML):
    IEEE 11073-20601 Regulatory Certification Data List (struct, variable)

The content of this characteristic is determined by the authorizing
organisation that provides certifications.  The internal structure
is defined by IEEE 11073-20601 and is opaque to the Bluetooth GATT
layer.  This implementation stores and returns the raw certification
data as bytes.

References:
    Bluetooth SIG Generic Attribute Profile
    org.bluetooth.characteristic.ieee_11073-20601_regulatory_certification_data_list
    IEEE 11073-20601
"""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class IEEE11073RegulatoryData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from IEEE 11073-20601 Regulatory Certification Data List.

    Attributes:
        certification_data: Raw certification data bytes as defined
            by the authorizing organisation per IEEE 11073-20601.

    """

    certification_data: bytes


class IEEE1107320601RegulatoryCharacteristic(
    BaseCharacteristic[IEEE11073RegulatoryData],
):
    """IEEE 11073-20601 Regulatory Certification Data List (0x2A2A).

    Contains regulatory and certification information in a format
    defined by IEEE 11073-20601.  The data is treated as opaque
    bytes by this library.
    """

    _characteristic_name = "IEEE 11073-20601 Regulatory Certification Data List"
    expected_type = IEEE11073RegulatoryData
    min_length: int = 1
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> IEEE11073RegulatoryData:
        """Parse IEEE 11073-20601 regulatory data from raw BLE bytes.

        Args:
            data: Raw bytearray containing certification data.
            ctx: Optional context (unused).
            validate: Whether to validate (unused for opaque data).

        Returns:
            IEEE11073RegulatoryData wrapping the raw bytes.

        """
        return IEEE11073RegulatoryData(certification_data=bytes(data))

    def _encode_value(self, data: IEEE11073RegulatoryData) -> bytearray:
        """Encode IEEE11073RegulatoryData back to BLE bytes.

        Args:
            data: IEEE11073RegulatoryData instance.

        Returns:
            Encoded bytearray containing the raw certification data.

        """
        return bytearray(data.certification_data)
