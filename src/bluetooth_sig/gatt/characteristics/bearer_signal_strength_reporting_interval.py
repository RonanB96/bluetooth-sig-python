"""Bearer Signal Strength Reporting Interval characteristic (0x2BB8)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class BearerSignalStrengthReportingIntervalCharacteristic(BaseCharacteristic[int]):
    """Bearer Signal Strength Reporting Interval characteristic (0x2BB8).

    org.bluetooth.characteristic.bearer_signal_strength_reporting_interval

    Reporting interval for signal strength, as an unsigned 8-bit integer (seconds).
    """

    _template = Uint8Template()
