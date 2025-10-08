"""Heat Index characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class HeatIndexCharacteristic(BaseCharacteristic):
    """Heat Index measurement characteristic."""

    _template = Uint8Template()
