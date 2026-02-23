"""Methane Concentration characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ConcentrationTemplate


class MethaneConcentrationCharacteristic(BaseCharacteristic[float]):
    """Methane concentration measurement characteristic (0x2BD1).

    Represents methane concentration in parts per million (ppm) with a
    resolution of 1 ppm.
    """

    _template = ConcentrationTemplate()

    _python_type: type | str | None = int
    _manual_unit: str = "ppm"  # Override template's "ppm" default

    # Template configuration
    resolution: float = 1.0
