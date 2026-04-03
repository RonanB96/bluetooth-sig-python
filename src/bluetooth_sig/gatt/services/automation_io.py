"""Automation IO Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class AutomationIOService(BaseGattService):
    """Automation IO Service implementation.

    Contains characteristics related to automation I/O.
    """

    _service_name: str | None = "Automation IO"

    # AIOS characteristics are conditionally required per service instance.
    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.DIGITAL: False,
        CharacteristicName.ANALOG: False,
        CharacteristicName.AGGREGATE: False,
    }
