"""Tx Power Level characteristic implementation."""

from dataclasses import dataclass

from .templates import SimpleSint8Characteristic


@dataclass
class TxPowerLevelCharacteristic(SimpleSint8Characteristic):
    """Tx Power Level characteristic.

    Measures transmit power level in dBm.
    """

    _characteristic_name: str = "Tx Power Level"
    
    # Template configuration
    measurement_unit: str = "dBm"
