"""Voltage Frequency characteristic implementation."""

from dataclasses import dataclass

from .templates import ScaledUint16Characteristic


@dataclass
class VoltageFrequencyCharacteristic(ScaledUint16Characteristic):
    """Voltage Frequency characteristic.

    Measures voltage frequency with 1/256 Hz resolution.
    """

    _characteristic_name: str = "Voltage Frequency"
    resolution: float = 1 / 256
    measurement_unit: str = "Hz"
