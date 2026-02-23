"""Percentage 8 Steps characteristic (0x2C05)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class Percentage8StepsCharacteristic(BaseCharacteristic[int]):
    """Percentage 8 Steps characteristic (0x2C05).

    org.bluetooth.characteristic.percentage_8_steps

    Number of steps from minimum to maximum value.
    M=1, d=0, b=0 — no scaling; plain unsigned 8-bit integer.
    Range: 1-200 (unitless).
    A value of 0xFF represents 'value is not known'.

    Raises:
        SpecialValueDetectedError: If raw value is a sentinel (e.g. 0xFF).
    """

    _template = Uint8Template()
