"""Stored Health Observations characteristic (0x2BDD).

Variable-length stored ACOM observation format (IEEE 11073-10101).

References:
    Bluetooth SIG Generic Health Sensor Service specification
"""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class StoredHealthObservationsCharacteristic(BaseCharacteristic[bytes]):
    """Stored Health Observations characteristic (0x2BDD).

    org.bluetooth.characteristic.stored_health_observations

    Variable-length stored health observation data using the ACOM
    encoding based on IEEE 11073-10101 nomenclature.
    """

    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bytes:
        return bytes(data)

    def _encode_value(self, data: bytes) -> bytearray:
        return bytearray(data)
