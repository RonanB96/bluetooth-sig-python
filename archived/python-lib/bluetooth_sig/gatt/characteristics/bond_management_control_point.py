"""Bond Management Control Point characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class BondManagementCommand(IntEnum):
    """Bond Management Control Point commands as per BMS v1.0 Table 3.3."""

    DELETE_BOND_OF_REQUESTING_DEVICE_BR_EDR_LE = 0x01
    DELETE_BOND_OF_REQUESTING_DEVICE_BR_EDR = 0x02
    DELETE_BOND_OF_REQUESTING_DEVICE_LE = 0x03
    DELETE_ALL_BONDS_ON_SERVER_BR_EDR_LE = 0x04
    DELETE_ALL_BONDS_ON_SERVER_BR_EDR = 0x05
    DELETE_ALL_BONDS_ON_SERVER_LE = 0x06
    DELETE_ALL_BUT_ACTIVE_BOND_ON_SERVER_BR_EDR_LE = 0x07
    DELETE_ALL_BUT_ACTIVE_BOND_ON_SERVER_BR_EDR = 0x08
    DELETE_ALL_BUT_ACTIVE_BOND_ON_SERVER_LE = 0x09


class BondManagementControlPointCharacteristic(BaseCharacteristic[BondManagementCommand]):
    """Bond Management Control Point characteristic (0x2AA4).

    org.bluetooth.characteristic.bond_management_control_point

    Write-only characteristic for sending bond management commands.
    Variable length, starting with command byte.
    """

    min_length = 1
    allow_variable_length = True
    _template = EnumTemplate.uint8(BondManagementCommand)
