"""GATT service typing definitions.

Strong typing for GATT services - no flexible dicts allowed!
NO LEGACY CODE SUPPORT - development phase only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from ..gatt.characteristics.base import BaseCharacteristic
from ..gatt.characteristics.registry import CharacteristicRegistry
from .gatt_enums import CharacteristicName

# Type variable for specific characteristic types
CharacteristicType = TypeVar("CharacteristicType", bound=BaseCharacteristic)


@dataclass(frozen=True)
class CharacteristicSpec(Generic[CharacteristicType]):
    """Specification for a single characteristic with strong typing.

    This provides compile-time type safety and IDE autocompletion
    for service characteristic definitions.

    Note: The characteristic name is derived from the dictionary key,
    eliminating redundancy and following DRY principles.
    """

    char_class: type[CharacteristicType]
    required: bool = False
    conditional: bool = False
    condition: str = ""


def characteristic(name: CharacteristicName, required: bool = False) -> CharacteristicSpec[BaseCharacteristic]:
    """Create a CharacteristicSpec using the central registry for class
    mapping.

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
CharacteristicCollection = dict[CharacteristicName, CharacteristicSpec[BaseCharacteristic]]
"""Maps characteristic names (enums) to their specifications - STRONG TYPING ONLY."""

# Network/protocol data structures - these are inherently dynamic from BLE
ServiceDiscoveryData = dict[str, dict[str, list[str]]]
"""Service discovery data: Service UUID -> characteristic properties."""

# Export helper function
__all__ = ["CharacteristicSpec", "CharacteristicCollection", "characteristic"]
