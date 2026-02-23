"""Estimated Service Date characteristic (0x2A86)."""

from __future__ import annotations

from datetime import date

from .base import BaseCharacteristic
from .templates import EpochDateTemplate


class EstimatedServiceDateCharacteristic(BaseCharacteristic[date]):
    """Estimated Service Date characteristic (0x2A86).

    org.bluetooth.characteristic.estimated_service_date

    Days elapsed since the Epoch (Jan 1, 1970) in UTC.
    Same encoding as Date UTC.
    """

    _template = EpochDateTemplate()
