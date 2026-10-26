"""Mesh Provisioning Data In characteristic implementation."""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic


class MeshProvisioningDataInCharacteristic(BaseCharacteristic[bytes]):
    """Mesh Provisioning Data In characteristic (0x2ADB).

    org.bluetooth.characteristic.mesh_provisioning_data_in

    Write-only characteristic for Mesh Provisioning PDU passthrough.
    Variable-length raw bytes written by the provisioner.
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
        """Pass through raw provisioning PDU bytes.

        Args:
            data: Raw bytes (variable length).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            Raw PDU bytes.

        """
        return bytes(data)

    def _encode_value(self, data: bytes) -> bytearray:
        """Encode raw provisioning PDU bytes.

        Args:
            data: Raw PDU bytes.

        Returns:
            Encoded bytearray.

        """
        return bytearray(data)
