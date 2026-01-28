"""PnP ID characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class VendorIdSource(IntEnum):
    """Vendor ID Source enumeration.

    Defines the namespace for the Vendor ID field.
    """

    RESERVED_0 = 0  # Reserved for Future Use
    BLUETOOTH_SIG = 1  # Bluetooth SIG Assigned Company Identifier
    USB_IF = 2  # USB Implementer's Forum assigned Vendor ID


class PnpIdData(msgspec.Struct, frozen=True, kw_only=True):
    """PnP ID data.

    Attributes:
        vendor_id_source: Vendor ID source namespace
        vendor_id: Vendor ID from the specified namespace
        product_id: Manufacturer managed identifier
        product_version: Manufacturer managed version
    """

    vendor_id_source: VendorIdSource
    vendor_id: int
    product_id: int
    product_version: int


class PnpIdCharacteristic(BaseCharacteristic[PnpIdData]):
    """PnP ID characteristic (0x2A50).

    org.bluetooth.characteristic.pnp_id

    Contains PnP ID information (7 bytes).
    """

    _manual_value_type = "PnpIdData"
    expected_length = 7

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> PnpIdData:
        """Parse PnP ID.

        Args:
            data: Raw bytearray (7 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True)

        Returns:
            PnpIdData with vendor_id_source, vendor_id, product_id, product_version.
        """
        return PnpIdData(
            vendor_id_source=VendorIdSource(data[0]),
            vendor_id=DataParser.parse_int16(data, 1, signed=False),
            product_id=DataParser.parse_int16(data, 3, signed=False),
            product_version=DataParser.parse_int16(data, 5, signed=False),
        )

    def _encode_value(self, data: PnpIdData) -> bytearray:
        """Encode PnP ID.

        Args:
            data: PnpIdData to encode

        Returns:
            Encoded bytes
        """
        result = bytearray()
        result.append(int(data.vendor_id_source))
        result.extend(DataParser.encode_int16(data.vendor_id, signed=False))
        result.extend(DataParser.encode_int16(data.product_id, signed=False))
        result.extend(DataParser.encode_int16(data.product_version, signed=False))
        return result
