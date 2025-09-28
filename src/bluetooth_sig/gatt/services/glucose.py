"""Glucose Service implementation."""

from dataclasses import dataclass
from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


@dataclass
class GlucoseService(BaseGattService):
    """Glucose Service implementation (0x1808).

    Used for glucose monitoring devices including continuous glucose
    monitors (CGMs) and traditional glucose meters. Provides
    comprehensive glucose measurement data with context and device
    capabilities.
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.GLUCOSE_MEASUREMENT: True,  # required
        CharacteristicName.GLUCOSE_FEATURE: True,  # required
        CharacteristicName.GLUCOSE_MEASUREMENT_CONTEXT: False,  # optional
    }
