"""GATT service typing definitions.

Strong typing for GATT services - no flexible dicts allowed!
NO LEGACY CODE SUPPORT - development phase only.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

import msgspec

from ..gatt.characteristics.base import BaseCharacteristic
from ..gatt.characteristics.registry import CharacteristicRegistry
from .data_types import CharacteristicInfo
from .gatt_enums import CharacteristicName
from .uuid import BluetoothUUID

# Type variable for specific characteristic types
CharacteristicTypeVar = TypeVar("CharacteristicTypeVar", bound=BaseCharacteristic[Any])


class CharacteristicSpec(msgspec.Struct, Generic[CharacteristicTypeVar], frozen=True, kw_only=True):
    """Specification for a single characteristic with strong typing.

    This provides compile-time type safety and IDE autocompletion
    for service characteristic definitions.

    Note: The characteristic name is derived from the dictionary key,
    eliminating redundancy and following DRY principles.
    """

    char_class: type[CharacteristicTypeVar]
    required: bool = False
    conditional: bool = False
    condition: str = ""


def characteristic(name: CharacteristicName, required: bool = False) -> CharacteristicSpec[BaseCharacteristic[Any]]:
    """Create a CharacteristicSpec using the central registry for class mapping.

    This eliminates the need to manually specify the characteristic class
    by automatically resolving it from the CharacteristicName enum.

    Args:
        name: The characteristic name enum
        required: Whether this characteristic is required

    Returns:
        A CharacteristicSpec with the appropriate class from the registry

    """
    char_class = CharacteristicRegistry.get_characteristic_class(name)
    if char_class is None:
        raise ValueError(f"No characteristic class found for {name}")

    return CharacteristicSpec(char_class=char_class, required=required)


# Strong type definitions - using enums instead of strings for type safety
CharacteristicCollection = dict[CharacteristicName, CharacteristicSpec[BaseCharacteristic[Any]]]
"""Maps characteristic names (enums) to their specifications - STRONG TYPING ONLY."""

# Network/protocol data structures - these are inherently dynamic from BLE
# Type aliases for service and characteristic discovery data
ServiceDiscoveryData = dict[BluetoothUUID, CharacteristicInfo]
"""Service discovery data: Service UUID -> characteristic discovery information."""

# Export helper function
__all__ = [
    "CharacteristicSpec",
    "CharacteristicTypeVar",
    "CharacteristicCollection",
    "ServiceDiscoveryData",
    "characteristic",
]
