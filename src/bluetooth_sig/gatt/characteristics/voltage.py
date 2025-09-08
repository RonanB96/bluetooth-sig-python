"""Voltage characteristic implementation."""

from dataclasses import dataclass

from .templates import ScaledUint16Characteristic


@dataclass
class VoltageCharacteristic(ScaledUint16Characteristic):
    """Voltage characteristic.

    Measures voltage with 1/64 V resolution.
    """

    _characteristic_name: str = "Voltage"
    
    # Template configuration
    resolution: float = 1/64  # 1/64 V resolution  
    measurement_unit: str = "V"
    max_value: float = 65535/64  # ~1024 V max
