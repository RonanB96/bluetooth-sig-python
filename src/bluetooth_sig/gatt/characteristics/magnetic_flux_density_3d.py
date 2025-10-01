"""Magnetic Flux Density 3D characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass, field

from ...types.gatt_enums import ValueType
from .templates import VectorCharacteristic


@dataclass
class MagneticFluxDensity3DCharacteristic(VectorCharacteristic):
    """Magnetic flux density 3D characteristic.

    Represents measurements of magnetic flux density for three
    orthogonal axes: X, Y, and Z. Note that 1 x 10^-7 Tesla equals 0.001
    Gauss.
    """

    _characteristic_name: str = "Magnetic Flux Density - 3D"
    _manual_value_type: ValueType | str | None = ValueType.STRING  # Override since decode_value returns dict
    _manual_unit: str | None = field(default="T", init=False)  # Override template's "units" default

    vector_components: list[str] = field(default_factory=lambda: ["x_axis", "y_axis", "z_axis"])
    resolution: float = 1e-7
