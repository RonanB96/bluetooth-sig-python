"""Analog characteristic (0x2A58)."""

from __future__ import annotations

from ...types import CharacteristicInfo
from ...types.uuid import BluetoothUUID
from .base import BaseCharacteristic
from .templates import Uint16Template


class AnalogCharacteristic(BaseCharacteristic[int]):
    """Analog characteristic (0x2A58).

    org.bluetooth.characteristic.analog

    Represents one analog signal value as an unsigned 16-bit integer.
    """

    _template = Uint16Template()
    expected_length = 2
    # TODO Remove once uuid is added to yaml files
    _info = CharacteristicInfo(
        uuid=BluetoothUUID(0x2A58),
        name="Analog",
        id="org.bluetooth.characteristic.analog",
        unit="",
    )
