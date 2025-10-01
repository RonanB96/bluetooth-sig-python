"""Tx Power Level characteristic implementation."""

from dataclasses import dataclass, field

from .templates import SimpleSint8Characteristic


@dataclass
class TxPowerLevelCharacteristic(SimpleSint8Characteristic):
    """Tx Power Level characteristic.

    Measures transmit power level in dBm.
    """

    _characteristic_name: str = "Tx Power Level"
    _manual_unit: str | None = field(default="dBm", init=False)  # Override template's "units" default
