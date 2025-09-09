"""Rainfall characteristic implementation."""

from dataclasses import dataclass

from .templates import RainfallCharacteristic as RainfallTemplate


@dataclass
class RainfallCharacteristic(RainfallTemplate):
    """Rainfall characteristic.

    Represents the amount of rain that has fallen in millimeters.
    """

    _characteristic_name: str = "Rainfall"
