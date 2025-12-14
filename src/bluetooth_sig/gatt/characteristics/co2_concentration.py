"""CO2 Concentration characteristic implementation."""

from __future__ import annotations

from ...types.gatt_enums import ValueType
from .base import BaseCharacteristic
from .templates import ConcentrationTemplate


class CO2ConcentrationCharacteristic(BaseCharacteristic):
    r"""Carbon Dioxide concentration characteristic (0x2B8C).

    YAML registry name uses LaTeX subscript form ("CO\\textsubscript{2} Concentration").
    We restore explicit `_characteristic_name` so UUID resolution succeeds because
    the automatic CamelCase splitter cannot derive the LaTeX form from the class name.

    Represents carbon dioxide concentration in parts per million (ppm)
    with a resolution of 1 ppm.
    """

    # Explicit YAML/registry name (contains LaTeX markup not derivable heuristically)
    _characteristic_name = "CO\\textsubscript{2} Concentration"

    _template = ConcentrationTemplate()

    _manual_value_type: ValueType | str | None = ValueType.INT
    _manual_unit: str | None = "ppm"  # Override template's "ppm" default

    # Template configuration
    resolution: float = 1.0
    max_value: int | float | None = 65533.0  # Exclude special values 0xFFFE and 0xFFFF

    expected_length: int = 2
    expected_type: type = int
