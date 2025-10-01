"""Non-Methane Volatile Organic Compounds Concentration characteristic
implementation."""

from dataclasses import dataclass, field

from .templates import IEEE11073FloatCharacteristic


@dataclass
class NonMethaneVOCConcentrationCharacteristic(IEEE11073FloatCharacteristic):
    """Non-Methane Volatile Organic Compounds concentration characteristic
    (0x2BD3).

    Uses IEEE 11073 SFLOAT format (medfloat16) as per SIG specification.
    Unit: kg/m³ (kilogram per cubic meter)
    """

    _characteristic_name: str = "Non-Methane Volatile Organic Compounds Concentration"
    _manual_unit: str | None = field(default="kg/m³", init=False)  # Unit as per SIG specification
