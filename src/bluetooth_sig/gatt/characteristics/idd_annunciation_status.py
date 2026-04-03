"""IDD Annunciation Status characteristic (0x2B22).

Reports alarm/reminder/status-change annunciations from the
Insulin Delivery Device.

References:
    Bluetooth SIG Insulin Delivery Service 1.0.1, Table 4.7
"""

from __future__ import annotations

from enum import IntEnum, IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class IDDAnnunciationFlags(IntFlag):
    """Flags indicating which fields are present."""

    ANNUNCIATION_PRESENT = 0x01
    AUX_INFO_1_PRESENT = 0x02
    AUX_INFO_2_PRESENT = 0x04
    AUX_INFO_3_PRESENT = 0x08
    AUX_INFO_4_PRESENT = 0x10
    AUX_INFO_5_PRESENT = 0x20


class IDDAnnunciationType(IntEnum):
    """IDD annunciation type (uint16 Hamming codes)."""

    SYSTEM_ISSUE = 0x000F
    MECHANICAL_ISSUE = 0x0033
    OCCLUSION_DETECTED = 0x003C
    RESERVOIR_ISSUE = 0x0055
    RESERVOIR_EMPTY = 0x005A
    RESERVOIR_LOW = 0x0066
    PRIMING_ISSUE = 0x0069
    INFUSION_SET_INCOMPLETE = 0x0096
    INFUSION_SET_DETACHED = 0x0099
    POWER_SOURCE_INSUFFICIENT = 0x00A5
    BATTERY_EMPTY = 0x00AA
    BATTERY_LOW = 0x00C3
    BATTERY_MEDIUM = 0x00CC
    BATTERY_FULL = 0x00F0
    TEMPERATURE_OUT_OF_RANGE = 0x00FF
    AIR_PRESSURE_OUT_OF_RANGE = 0x0303
    BOLUS_CANCELED = 0x030C
    TBR_OVER = 0x0330
    TBR_CANCELED = 0x033F
    MAX_DELIVERY = 0x0356
    DATE_TIME_ISSUE = 0x0359
    TEMPERATURE = 0x0365


class IDDAnnunciationStatus(IntEnum):
    """IDD annunciation status (uint8 Hamming codes)."""

    UNDETERMINED = 0x0F
    PENDING = 0x33
    SNOOZED = 0x3C
    CONFIRMED = 0x55


class IDDAnnunciationStatusData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from IDD Annunciation Status characteristic.

    Attributes:
        flags: Bit field indicating which optional fields are present.
        annunciation_instance_id: Instance identifier for this annunciation.
        annunciation_type: Type of annunciation (Hamming-coded).
        annunciation_status: Current status of the annunciation.
        aux_info: Up to 5 auxiliary info uint16 values.

    """

    flags: IDDAnnunciationFlags
    annunciation_instance_id: int | None = None
    annunciation_type: IDDAnnunciationType | None = None
    annunciation_status: IDDAnnunciationStatus | None = None
    aux_info: list[int] = []


_AUX_FLAGS = [
    IDDAnnunciationFlags.AUX_INFO_1_PRESENT,
    IDDAnnunciationFlags.AUX_INFO_2_PRESENT,
    IDDAnnunciationFlags.AUX_INFO_3_PRESENT,
    IDDAnnunciationFlags.AUX_INFO_4_PRESENT,
    IDDAnnunciationFlags.AUX_INFO_5_PRESENT,
]


class IDDAnnunciationStatusCharacteristic(BaseCharacteristic[IDDAnnunciationStatusData]):
    """IDD Annunciation Status characteristic (0x2B22).

    org.bluetooth.characteristic.idd_annunciation_status

    Reports annunciation (alert/reminder/status) information
    from the Insulin Delivery Device.
    """

    min_length = 1  # flags only
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IDDAnnunciationStatusData:
        """Parse IDD Annunciation Status data.

        Format: Flags(uint8) + [InstanceID(uint16) + Type(uint16) + Status(uint8)]
                + [AuxInfo1(uint16)] ... [AuxInfo5(uint16)]
        """
        flags = IDDAnnunciationFlags(DataParser.parse_int8(data, 0, signed=False))
        offset = 1

        instance_id: int | None = None
        annunciation_type: IDDAnnunciationType | None = None
        annunciation_status: IDDAnnunciationStatus | None = None

        if flags & IDDAnnunciationFlags.ANNUNCIATION_PRESENT:
            instance_id = DataParser.parse_int16(data, offset, signed=False)
            annunciation_type = IDDAnnunciationType(DataParser.parse_int16(data, offset + 2, signed=False))
            annunciation_status = IDDAnnunciationStatus(DataParser.parse_int8(data, offset + 4, signed=False))
            offset += 5

        aux_info: list[int] = []
        for aux_flag in _AUX_FLAGS:
            if flags & aux_flag:
                aux_info.append(DataParser.parse_int16(data, offset, signed=False))
                offset += 2

        return IDDAnnunciationStatusData(
            flags=flags,
            annunciation_instance_id=instance_id,
            annunciation_type=annunciation_type,
            annunciation_status=annunciation_status,
            aux_info=aux_info,
        )

    def _encode_value(self, data: IDDAnnunciationStatusData) -> bytearray:
        """Encode IDD Annunciation Status data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.flags), signed=False))

        if data.flags & IDDAnnunciationFlags.ANNUNCIATION_PRESENT:
            result.extend(DataParser.encode_int16(data.annunciation_instance_id or 0, signed=False))
            result.extend(DataParser.encode_int16(int(data.annunciation_type or 0), signed=False))
            result.extend(DataParser.encode_int8(int(data.annunciation_status or 0), signed=False))

        for value in data.aux_info:
            result.extend(DataParser.encode_int16(value, signed=False))

        return result
