"""Link Loss Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class LinkLossService(BaseGattService):
    """Link Loss Service implementation.

    Defines behaviour when a link is lost between two devices.

    Contains characteristics related to link loss alerts:
    - Alert Level - Required
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.ALERT_LEVEL: True,  # required
    }
