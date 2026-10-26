"""Mesh Proxy Data In characteristic implementation."""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic


class MeshProxyDataInCharacteristic(BaseCharacteristic[bytes]):
    """Mesh Proxy Data In characteristic (0x2ADD).

    org.bluetooth.characteristic.mesh_proxy_data_in

    Write-only characteristic for Mesh Proxy PDU passthrough.
    Variable-length raw bytes written by the proxy client.
    """

    _manual_role = CharacteristicRole.CONTROL
    min_length: int = 1
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> bytes:
        """Pass through raw proxy PDU bytes.

        Args:
            data: Raw bytes (variable length).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            Raw PDU bytes.

        """
        return bytes(data)

    def _encode_value(self, data: bytes) -> bytearray:
        """Encode raw proxy PDU bytes.

        Args:
            data: Raw PDU bytes.

        Returns:
            Encoded bytearray.

        """
        return bytearray(data)
