"""Nitrogen Dioxide Concentration characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ConcentrationTemplate


class NitrogenDioxideConcentrationCharacteristic(BaseCharacteristic[float]):
    """Nitrogen dioxide concentration measurement characteristic (0x2BD2).

    Represents nitrogen dioxide (NO2) concentration in parts per billion
    (ppb) with a resolution of 1 ppb.
    """

    _template = ConcentrationTemplate()

    _manual_unit: str = "ppb"  # Override template's "ppm" default

    # Template configuration
    resolution: float = 1.0
