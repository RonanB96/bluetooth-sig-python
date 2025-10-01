"""Ammonia Concentration characteristic implementation."""

from dataclasses import dataclass, field

from .templates import IEEE11073FloatCharacteristic


@dataclass
class AmmoniaConcentrationCharacteristic(IEEE11073FloatCharacteristic):
    """Ammonia concentration measurement characteristic (0x2BCF).

    Uses IEEE 11073 SFLOAT format (medfloat16) as per SIG specification.
    Unit: kg/m³ (kilogram per cubic meter)
    """

    _characteristic_name: str = "Ammonia Concentration"
    _manual_unit: str | None = field(default="kg/m³", init=False)  # Unit as per SIG specification
