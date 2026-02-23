"""PM10 Concentration characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ConcentrationTemplate


class PM10ConcentrationCharacteristic(BaseCharacteristic[float]):
    """PM10 particulate matter concentration characteristic (0x2BD7).

    Represents particulate matter PM10 concentration in micrograms per
    cubic meter with a resolution of 1 μg/m³.
    """

    _template = ConcentrationTemplate()

    _characteristic_name: str = "Particulate Matter - PM10 Concentration"
    _python_type: type | str | None = int
    _manual_unit: str = "µg/m³"  # Override template's "ppm" default

    # Template configuration
    resolution: float = 1.0
