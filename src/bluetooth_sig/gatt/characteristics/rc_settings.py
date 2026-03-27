"""RC Settings characteristic (0x2B1E).

Reconnection Configuration settings value.

The Reconnection Configuration Service 1.0 has been **Withdrawn** by BT SIG,
so the full field-level spec is no longer available. The characteristic is
retained as a plain uint16 because no authoritative bitfield definition can
be verified.

References:
    Bluetooth SIG Reconnection Configuration Service 1.0 (Withdrawn)
"""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint16Template


class RCSettingsCharacteristic(BaseCharacteristic[int]):
    """RC Settings characteristic (0x2B1E).

    org.bluetooth.characteristic.rc_settings

    Reconnection configuration settings stored as a uint16 value.
    """

    _template = Uint16Template()
