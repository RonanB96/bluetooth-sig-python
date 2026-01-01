"""Bond Management Control Point characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


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
    _template = EnumTemplate.uint8(BondManagementCommand)
