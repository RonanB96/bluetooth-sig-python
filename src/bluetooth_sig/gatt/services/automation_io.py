"""Automation IO Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class AutomationIOService(BaseGattService):
    """Automation IO Service implementation.

    Contains characteristics related to electrical power monitoring and automation:
    - Electric Current - Optional
    - Voltage - Optional
    - Average Current - Optional
    - Average Voltage - Optional
    - Electric Current Range - Optional
    - Electric Current Specification - Optional
    - Electric Current Statistics - Optional
    - Voltage Specification - Optional
    - Voltage Statistics - Optional
    - High Voltage - Optional
    - Voltage Frequency - Optional
    - Supported Power Range - Optional
    - Tx Power Level - Optional
    """

    _service_name: str = "Automation IO"

    # Will be populated as we implement each characteristic
    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.ELECTRIC_CURRENT: False,  # optional
        CharacteristicName.VOLTAGE: False,  # optional
        CharacteristicName.AVERAGE_CURRENT: False,  # optional
        CharacteristicName.AVERAGE_VOLTAGE: False,  # optional
    }
