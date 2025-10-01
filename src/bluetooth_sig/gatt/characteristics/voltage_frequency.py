"""Voltage Frequency characteristic implementation."""

from dataclasses import dataclass, field

from .templates import ScaledUint16Characteristic


@dataclass
class VoltageFrequencyCharacteristic(ScaledUint16Characteristic):
    """Voltage Frequency characteristic.

    Measures voltage frequency with 1/256 Hz resolution.
    """

    _characteristic_name: str = "Voltage Frequency"
    _manual_unit: str | None = field(default="Hz", init=False)  # Override template's "units" default
    resolution: float = 1 / 256
