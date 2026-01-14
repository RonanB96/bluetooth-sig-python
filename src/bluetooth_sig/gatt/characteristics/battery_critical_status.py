"""Battery Critical Status characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser


class BatteryCriticalStatus(msgspec.Struct):
    """Battery Critical Status data structure."""

    critical_power_state: bool
    immediate_service_required: bool


class BatteryCriticalStatusValues(IntFlag):  # pylint: disable=too-few-public-methods
    """Bit mask constants for Battery Critical Status characteristic."""

    CRITICAL_POWER_STATE_MASK = 0x01
    IMMEDIATE_SERVICE_REQUIRED_MASK = 0x02


class BatteryCriticalStatusCharacteristic(BaseCharacteristic[BatteryCriticalStatus]):
    """Battery Critical Status characteristic."""

    _manual_unit: str | None = None  # Bitfield, no units

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> BatteryCriticalStatus:
        """Decode the battery critical status value."""
        value = DataParser.parse_int8(data, 0, signed=False)

        return BatteryCriticalStatus(
            critical_power_state=bool(value & BatteryCriticalStatusValues.CRITICAL_POWER_STATE_MASK),
            immediate_service_required=bool(value & BatteryCriticalStatusValues.IMMEDIATE_SERVICE_REQUIRED_MASK),
        )

    def _encode_value(self, data: BatteryCriticalStatus) -> bytearray:
        """Encode the battery critical status value."""
        encoded = 0
        if data.critical_power_state:
            encoded |= BatteryCriticalStatusValues.CRITICAL_POWER_STATE_MASK
        if data.immediate_service_required:
            encoded |= BatteryCriticalStatusValues.IMMEDIATE_SERVICE_REQUIRED_MASK

        return DataParser.encode_int8(encoded, signed=False)
