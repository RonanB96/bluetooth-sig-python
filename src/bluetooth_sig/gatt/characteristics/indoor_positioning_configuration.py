"""Indoor Positioning Configuration characteristic implementation."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class IndoorPositioningConfigurationCharacteristic(BaseCharacteristic):
    """Indoor Positioning Configuration characteristic (0x2AAD).

    org.bluetooth.characteristic.indoor_positioning_configuration

    Indoor Positioning Configuration characteristic.
    """

    expected_length = 1
    min_value = 0
    max_value = UINT8_MAX
    expected_type = int

    _template = Uint8Template()
