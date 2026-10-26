"""Cooking Zone Desired Cooking Conditions characteristic (0x2C2A)."""

from __future__ import annotations

from ..constants import SIZE_UINT16
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .cooking_common import CookingConditionsData, encode_cooking_conditions, parse_cooking_conditions


class CookingZoneDesiredCookingConditionsCharacteristic(BaseCharacteristic[CookingConditionsData]):
    """Cooking Zone Desired Cooking Conditions characteristic (0x2C2A).

    org.bluetooth.characteristic.cooking_zone_desired_cooking_conditions
    """

    min_length = SIZE_UINT16
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> CookingConditionsData:
        return parse_cooking_conditions(data)

    def _encode_value(self, data: CookingConditionsData) -> bytearray:
        return encode_cooking_conditions(data)
