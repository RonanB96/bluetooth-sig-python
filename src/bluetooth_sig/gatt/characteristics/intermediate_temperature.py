"""Intermediate Temperature characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import IEEE11073FloatTemplate


class IntermediateTemperatureCharacteristic(BaseCharacteristic[float]):
    """Intermediate Temperature characteristic (0x2A1E).

    org.bluetooth.characteristic.intermediate_temperature

    Represents an intermediate temperature measurement using IEEE-11073 FLOAT format.
    """

    _template = IEEE11073FloatTemplate()
