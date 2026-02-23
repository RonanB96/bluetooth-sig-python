"""System ID characteristic implementation."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class SystemIdData(msgspec.Struct, frozen=True, kw_only=True):
    """System ID data.

    Attributes:
        manufacturer_id: 40-bit manufacturer identifier
        oui: 24-bit organizationally unique identifier
    """

    manufacturer_id: bytes
    oui: bytes


class SystemIdCharacteristic(BaseCharacteristic[SystemIdData]):
    """System ID characteristic (0x2A23).

    org.bluetooth.characteristic.system_id

    Represents a 64-bit system identifier: 40-bit manufacturer ID + 24-bit organizationally unique ID.
    """

    expected_length = 8

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> SystemIdData:
        """Parse System ID.

        Args:
            data: Raw bytearray (8 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True)

        Returns:
            SystemIdData with manufacturer_id (5 bytes) and oui (3 bytes).
        """
        return SystemIdData(
            manufacturer_id=bytes(data[0:5]),
            oui=bytes(data[5:8]),
        )

    def _encode_value(self, data: SystemIdData) -> bytearray:
        """Encode System ID.

        Args:
            data: SystemIdData to encode

        Returns:
            Encoded bytes
        """
        result = bytearray()
        result.extend(data.manufacturer_id)
        result.extend(data.oui)
        return result
