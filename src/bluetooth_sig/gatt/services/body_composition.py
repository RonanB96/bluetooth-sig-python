"""Body Composition Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class BodyCompositionService(BaseGattService):
    """Body Composition Service implementation (0x181B).

    Used for smart scale devices that measure body composition metrics
    including body fat percentage, muscle mass, bone mass, and water
    percentage. Contains Body Composition Measurement and Body
    Composition Feature characteristics.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.BODY_COMPOSITION_MEASUREMENT: True,  # required
        CharacteristicName.BODY_COMPOSITION_FEATURE: False,  # optional
    }
