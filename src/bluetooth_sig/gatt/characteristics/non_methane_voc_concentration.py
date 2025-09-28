"""Non-Methane Volatile Organic Compounds Concentration characteristic
implementation."""

from dataclasses import dataclass

from .templates import IEEE11073FloatCharacteristic


@dataclass
class NonMethaneVOCConcentrationCharacteristic(IEEE11073FloatCharacteristic):
    """Non-Methane Volatile Organic Compounds concentration characteristic
    (0x2BD3).

    Uses IEEE 11073 SFLOAT format (medfloat16) as per SIG specification.
    Unit: kg/m³ (kilogram per cubic meter)
    """

    _characteristic_name: str = "Non-Methane Volatile Organic Compounds Concentration"

    @property
    def unit(self) -> str:
        """Return unit as per SIG specification."""
        return "kg/m³"
