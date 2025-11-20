"""Pulse Oximeter Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class PulseOximeterService(BaseGattService):
    """Pulse Oximeter Service implementation.

    Contains characteristics related to pulse oximetry:
    - PLX Spot-Check Measurement - Optional
    - PLX Continuous Measurement - Optional
    - PLX Features - Mandatory
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.PLX_SPOT_CHECK_MEASUREMENT: False,  # optional
        CharacteristicName.PLX_CONTINUOUS_MEASUREMENT: False,  # optional
        CharacteristicName.PLX_FEATURES: True,  # mandatory
    }
