"""Ranging Data Ready characteristic (0x2C18).

Per RAS v1.0 §3.4, Table 3.14: contains only the Ranging Counter (uint16)
of the completed CS Procedure.

References:
    Bluetooth SIG Ranging Service v1.0, Section 3.4
"""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from .base import BaseCharacteristic
from .templates import Uint16Template


class RangingDataReadyCharacteristic(BaseCharacteristic[int]):
    """Ranging Data Ready characteristic (0x2C18).

    org.bluetooth.characteristic.ranging_data_ready

    Indicates that ranging data is ready for retrieval.
    The value is the Ranging Counter of the completed CS Procedure.
    """

    _manual_role = CharacteristicRole.STATUS
    _template = Uint16Template()
