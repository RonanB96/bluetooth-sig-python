"""Bond Management Control Point characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class BondManagementCommand(IntEnum):
    """Bond Management Control Point commands."""

    DELETE_BOND_OF_REQUESTING_DEVICE = 0x01
    DELETE_ALL_BONDS_ON_SERVER = 0x02
    DELETE_ALL_BUT_ACTIVE_BOND_ON_SERVER = 0x03


class BondManagementControlPointCharacteristic(BaseCharacteristic):
    """Bond Management Control Point characteristic (0x2AA4).

    org.bluetooth.characteristic.bond_management_control_point

    Write-only characteristic for sending bond management commands.
    Variable length, starting with command byte.
    """

    min_length = 1
    allow_variable_length = True

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> BondManagementCommand:
        """Decode Bond Management Control Point data from bytes.

        Args:
            data: Raw characteristic data (at least 1 byte)
            ctx: Optional characteristic context

        Returns:
            BondManagementCommand

        Raises:
            ValueError: If data is insufficient or command invalid

        """
        if len(data) < 1:
            raise ValueError("Insufficient data for Bond Management Control Point: expected at least 1 byte")

        # Parse command (1 byte)
        command_value = data[0]
        try:
            command = BondManagementCommand(command_value)
        except ValueError as exc:
            raise ValueError(f"Invalid command: {command_value}") from exc

        return command

    def encode_value(self, data: BondManagementCommand) -> bytearray:
        """Encode Bond Management Control Point data to bytes.

        Args:
            data: BondManagementCommand to encode
        Returns:
            Encoded command (1 byte)

        """
        result = bytearray()
        result.append(data.value)
        return result
