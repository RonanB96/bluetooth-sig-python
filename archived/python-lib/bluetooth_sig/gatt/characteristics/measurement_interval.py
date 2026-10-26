"""Measurement Interval characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint16Template


class MeasurementIntervalCharacteristic(BaseCharacteristic[int]):
    """Measurement Interval characteristic (0x2A21).

    org.bluetooth.characteristic.measurement_interval

    Represents the measurement interval in seconds as a 16-bit unsigned integer.
    """

    _template = Uint16Template()
