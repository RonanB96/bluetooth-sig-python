"""Caloric Intake characteristic (0x2B45)."""

from .base import BaseCharacteristic
from .templates import Uint16Template


class CaloricIntakeCharacteristic(BaseCharacteristic):
    """Caloric Intake characteristic (0x2B45).

    org.bluetooth.characteristic.caloric_intake

    Caloric Intake characteristic.
    """

    _template = Uint16Template()
