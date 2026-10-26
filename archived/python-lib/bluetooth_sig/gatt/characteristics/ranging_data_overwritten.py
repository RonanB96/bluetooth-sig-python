"""Ranging Data Overwritten characteristic (0x2C19).

Per RAS v1.0 §3.5, Table 3.15: contains only the Ranging Counter (uint16)
of the CS Ranging Data that was overwritten.

References:
    Bluetooth SIG Ranging Service v1.0, Section 3.5
"""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from .base import BaseCharacteristic
from .templates import Uint16Template


class RangingDataOverwrittenCharacteristic(BaseCharacteristic[int]):
    """Ranging Data Overwritten characteristic (0x2C19).

    org.bluetooth.characteristic.ranging_data_overwritten

    Indicates that ranging data has been overwritten.
    The value is the Ranging Counter of the overwritten CS Procedure.
    """

    _manual_role = CharacteristicRole.STATUS
    _template = Uint16Template()
