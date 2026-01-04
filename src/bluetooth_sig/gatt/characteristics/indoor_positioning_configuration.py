"""Indoor Positioning Configuration characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class IndoorPositioningConfigurationCharacteristic(BaseCharacteristic[int]):
    """Indoor Positioning Configuration characteristic (0x2AAD).

    org.bluetooth.characteristic.indoor_positioning_configuration

    Indoor Positioning Configuration characteristic.
    """

    _template = Uint8Template()
