"""Generic Attribute Service implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


@dataclass
class GenericAttributeService(BaseGattService):
    """Generic Attribute Service implementation.

    The GATT Service contains information about the GATT database and is
    primarily used for service discovery and attribute access.

    This service typically contains:
    - Service Changed characteristic (optional)
    """

    _service_name: str = "GATT"

    # This service has no standard characteristics defined yet
    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {}
