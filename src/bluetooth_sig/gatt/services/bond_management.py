"""Bond Management Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class BondManagementService(BaseGattService):
    """Bond Management Service implementation.

    Contains characteristics for managing Bluetooth bonds:
    - Bond Management Feature - Required
    - Bond Management Control Point - Required
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.BOND_MANAGEMENT_FEATURE: True,  # required
        CharacteristicName.BOND_MANAGEMENT_CONTROL_POINT: True,  # required
    }
