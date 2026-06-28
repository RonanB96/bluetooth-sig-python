"""Cookware Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class CookwareService(BaseGattService):
    """Cookware Service implementation (0x185D).

    Per Cookware Service spec Table 3.1:
    - Mandatory: Cookware Description, Cookware Sensor Data
    - Conditional (C.1/C.2): recipe/zone characteristics when control loop or
      multiple sensors apply — modeled as optional for discovery validation
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.COOKWARE_DESCRIPTION: True,
        CharacteristicName.COOKWARE_SENSOR_DATA: True,
        CharacteristicName.RECIPE_PARAMETERS: False,
        CharacteristicName.RECIPE_CONTROL: False,
        CharacteristicName.COOKING_STEP_STATUS: False,
        CharacteristicName.COOKING_ZONE_CAPABILITIES: False,
        CharacteristicName.COOKING_ZONE_DESIRED_COOKING_CONDITIONS: False,
        CharacteristicName.COOKING_ZONE_ACTUAL_COOKING_CONDITIONS: False,
        CharacteristicName.COOKWARE_SENSOR_AGGREGATE: False,
    }
