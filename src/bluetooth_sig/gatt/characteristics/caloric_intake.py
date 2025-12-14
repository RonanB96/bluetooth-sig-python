"""Caloric Intake characteristic (0x2B45)."""

from __future__ import annotations

from ..constants import UINT16_MAX
from .base import BaseCharacteristic
from .templates import Uint16Template


class CaloricIntakeCharacteristic(BaseCharacteristic):
    """Caloric Intake characteristic (0x2B45).

    org.bluetooth.characteristic.caloric_intake

    Caloric Intake characteristic.
    """

    # Validation attributes
    expected_length: int = 2  # uint16
    min_value: int = 0
    max_value: int = UINT16_MAX
    expected_type: type = int

    _template = Uint16Template()
