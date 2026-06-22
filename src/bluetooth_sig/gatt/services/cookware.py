"""Cookware Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class CookwareService(BaseGattService):
    """Cookware Service implementation (0x185D)."""

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.COOKWARE_DESCRIPTION: True,
        CharacteristicName.RECIPE_CONTROL: True,
        CharacteristicName.RECIPE_PARAMETERS: True,
        CharacteristicName.COOKING_STEP_STATUS: True,
        CharacteristicName.COOKING_ZONE_CAPABILITIES: True,
        CharacteristicName.COOKING_ZONE_DESIRED_COOKING_CONDITIONS: True,
        CharacteristicName.COOKING_ZONE_ACTUAL_COOKING_CONDITIONS: True,
        CharacteristicName.COOKWARE_SENSOR_DATA: True,
        CharacteristicName.COOKWARE_SENSOR_AGGREGATE: True,
        CharacteristicName.COOKING_TEMPERATURE: True,
        CharacteristicName.COOKING_ZONE_PERCEIVED_POWER: True,
        CharacteristicName.KITCHEN_APPLIANCE_AIRFLOW: True,
    }
