"""Tx Power Level characteristic implementation."""

from __future__ import annotations

from ...types.units import ElectricalUnit
from .base import BaseCharacteristic
from .templates import Sint8Template


class TxPowerLevelCharacteristic(BaseCharacteristic):
    """Tx Power Level characteristic (0x2A07).

    org.bluetooth.characteristic.tx_power_level

    Tx Power Level characteristic.

    Measures transmit power level in dBm.
    """

    _template = Sint8Template()

    _characteristic_name: str = "Tx Power Level"
    _manual_unit: str = ElectricalUnit.DBM.value  # Override template's "units" default

    # Validation attributes
