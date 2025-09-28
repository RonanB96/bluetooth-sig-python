"""Magnetic Flux Density 2D characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass, field

from .templates import Vector2DCharacteristic


@dataclass
class MagneticFluxDensity2DCharacteristic(Vector2DCharacteristic):
    """Magnetic flux density 2D characteristic.

    Represents measurements of magnetic flux density for two orthogonal
    axes: X and Y. Note that 1 x 10^-7 Tesla equals 0.001 Gauss.
    """

    _characteristic_name: str = "Magnetic Flux Density - 2D"
    _manual_value_type: str = "string"  # Override since decode_value returns dict

    vector_components: list[str] = field(default_factory=lambda: ["x_axis", "y_axis"])
    component_unit: str = "T"
    resolution: float = 1e-7
