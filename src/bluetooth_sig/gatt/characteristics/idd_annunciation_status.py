"""IDD Annunciation Status characteristic (0x2B22).

Reports alarm/reminder/status-change annunciations from the
Insulin Delivery Device.

References:
    Bluetooth SIG Insulin Delivery Service 1.0
"""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class IDDAnnunciationType(IntEnum):
    """IDD annunciation type."""

    ALERT = 0x01
    REMINDER = 0x02
    STATUS_CHANGED = 0x03


class IDDAnnunciationStatus(IntEnum):
    """IDD annunciation status."""

    PENDING = 0x00
    ACTIVE = 0x01
    AUXILIARY = 0x02


class IDDAnnunciationStatusData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from IDD Annunciation Status characteristic.

    Attributes:
        annunciation_instance_id: Instance identifier for this annunciation.
        annunciation_type: Type of annunciation (alert/reminder/status changed).
        annunciation_status: Current status of the annunciation.

    """

    annunciation_instance_id: int
    annunciation_type: IDDAnnunciationType
    annunciation_status: IDDAnnunciationStatus


class IDDAnnunciationStatusCharacteristic(BaseCharacteristic[IDDAnnunciationStatusData]):
    """IDD Annunciation Status characteristic (0x2B22).

    org.bluetooth.characteristic.idd_annunciation_status

    Reports annunciation (alert/reminder/status) information
    from the Insulin Delivery Device.
    """

    min_length = 4  # instance_id(2) + type(1) + status(1)
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IDDAnnunciationStatusData:
        """Parse IDD Annunciation Status data.

        Format: AnnunciationInstanceID (uint16) + AnnunciationType (uint8)
                + AnnunciationStatus (uint8).
        """
        instance_id = DataParser.parse_int16(data, 0, signed=False)
        annunciation_type = IDDAnnunciationType(DataParser.parse_int8(data, 2, signed=False))
        annunciation_status = IDDAnnunciationStatus(DataParser.parse_int8(data, 3, signed=False))

        return IDDAnnunciationStatusData(
            annunciation_instance_id=instance_id,
            annunciation_type=annunciation_type,
            annunciation_status=annunciation_status,
        )

    def _encode_value(self, data: IDDAnnunciationStatusData) -> bytearray:
        """Encode IDD Annunciation Status data."""
        result = bytearray()
        result.extend(DataParser.encode_int16(data.annunciation_instance_id, signed=False))
        result.extend(DataParser.encode_int8(int(data.annunciation_type), signed=False))
        result.extend(DataParser.encode_int8(int(data.annunciation_status), signed=False))
        return result
