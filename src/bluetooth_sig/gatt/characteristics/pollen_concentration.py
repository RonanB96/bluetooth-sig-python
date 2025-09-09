"""Pollen Concentration characteristic implementation."""

from dataclasses import dataclass

from .templates import Uint24ScaledCharacteristic


@dataclass
class PollenConcentrationCharacteristic(Uint24ScaledCharacteristic):
    """Pollen concentration measurement characteristic (0x2A75).

    Uses uint24 format as per SIG specification.
    Unit: grains/m³ (count per cubic meter)
    """

    _characteristic_name: str = "Pollen Concentration"
    _manual_value_type: str = (
        "float"  # Override YAML spec since decode_value returns float
    )

    # SIG specification configuration
    resolution: float = 1.0
    measurement_unit: str = "grains/m³"
