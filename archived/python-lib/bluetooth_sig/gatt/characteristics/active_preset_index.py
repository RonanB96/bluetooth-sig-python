"""Active Preset Index characteristic (0x2BDC)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class ActivePresetIndexCharacteristic(BaseCharacteristic[int]):
    """Active Preset Index characteristic (0x2BDC).

    org.bluetooth.characteristic.active_preset_index

    Index of the currently active preset.
    """

    _template = Uint8Template()
