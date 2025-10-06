"""Dew Point characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Sint8Template


class DewPointCharacteristic(BaseCharacteristic):
    """Dew Point measurement characteristic."""

    _template = Sint8Template()

    _characteristic_name: str = "Dew Point"
