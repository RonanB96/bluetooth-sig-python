"""Generic Access Service implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


@dataclass
class GenericAccessService(BaseGattService):
    """Generic Access Service implementation.

    Contains characteristics that expose basic device access information:
    - Device Name - Required
    - Appearance - Optional
    """

    _service_name: str = "GAP"

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.DEVICE_NAME: True,  # required
        CharacteristicName.APPEARANCE: False,  # optional
    }
