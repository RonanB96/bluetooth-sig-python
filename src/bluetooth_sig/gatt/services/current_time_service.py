"""Current Time Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class CurrentTimeService(BaseGattService):
    """Current Time Service implementation.

    Exposes the current date and time with additional information.

    Contains characteristics related to time:
    - Current Time - Required
    - Local Time Information - Optional
    - Reference Time Information - Optional
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.CURRENT_TIME: True,  # required
        CharacteristicName.LOCAL_TIME_INFORMATION: False,  # optional
        CharacteristicName.REFERENCE_TIME_INFORMATION: False,  # optional
    }
