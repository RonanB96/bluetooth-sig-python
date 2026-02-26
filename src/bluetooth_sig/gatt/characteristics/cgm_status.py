"""CGM Status characteristic implementation.

Implements the CGM Status characteristic (0x2AA9).  Reports the current
status of a CGM sensor.

Structure (from GSS YAML):
    Time Offset (uint16) -- minutes since session start
    CGM Status (3 bytes, boolean[24]) -- always 3 octets
    E2E-CRC (uint16, optional) -- present if E2E-CRC Supported

The 24-bit status uses the same bit definitions as CGM Measurement's
Sensor Status Annunciation (Status + Cal/Temp + Warning).

References:
    Bluetooth SIG Continuous Glucose Monitoring Service
    org.bluetooth.characteristic.cgm_status (GSS YAML)
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class CGMStatusFlags(IntFlag):
    """CGM Status flags (24-bit).

    Combined Status (bits 0-7), Cal/Temp (bits 8-15), and Warning (bits 16-23).
    """

    # Status octet (bits 0-7)
    SESSION_STOPPED = 0x000001
    DEVICE_BATTERY_LOW = 0x000002
    SENSOR_TYPE_INCORRECT = 0x000004
    SENSOR_MALFUNCTION = 0x000008
    DEVICE_SPECIFIC_ALERT = 0x000010
    GENERAL_DEVICE_FAULT = 0x000020
    # Cal/Temp octet (bits 8-15)
    TIME_SYNC_REQUIRED = 0x000100
    CALIBRATION_NOT_ALLOWED = 0x000200
    CALIBRATION_RECOMMENDED = 0x000400
    CALIBRATION_REQUIRED = 0x000800
    SENSOR_TEMP_TOO_HIGH = 0x001000
    SENSOR_TEMP_TOO_LOW = 0x002000
    CALIBRATION_PENDING = 0x004000
    # Warning octet (bits 16-23)
    RESULT_LOWER_THAN_PATIENT_LOW = 0x010000
    RESULT_HIGHER_THAN_PATIENT_HIGH = 0x020000
    RESULT_LOWER_THAN_HYPO = 0x040000
    RESULT_HIGHER_THAN_HYPER = 0x080000
    RATE_OF_DECREASE_EXCEEDED = 0x100000
    RATE_OF_INCREASE_EXCEEDED = 0x200000
    RESULT_LOWER_THAN_DEVICE_CAN_PROCESS = 0x400000
    RESULT_HIGHER_THAN_DEVICE_CAN_PROCESS = 0x800000


class CGMStatusData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from CGM Status characteristic.

    Attributes:
        time_offset: Minutes since session start.
        status: 24-bit combined status flags.
        e2e_crc: E2E-CRC value. None if absent.

    """

    time_offset: int
    status: CGMStatusFlags
    e2e_crc: int | None = None


class CGMStatusCharacteristic(BaseCharacteristic[CGMStatusData]):
    """CGM Status characteristic (0x2AA9).

    Reports current CGM sensor status with 24-bit status flags
    and optional E2E-CRC.
    """

    expected_type = CGMStatusData
    min_length: int = 5  # time_offset(2) + status(3)
    allow_variable_length: bool = True  # optional E2E-CRC

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> CGMStatusData:
        """Parse CGM Status from raw BLE bytes.

        Args:
            data: Raw bytearray from BLE characteristic (5 or 7 bytes).
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            CGMStatusData with time offset and status flags.

        """
        time_offset = DataParser.parse_int16(data, 0, signed=False)
        status_raw = data[2] | (data[3] << 8) | (data[4] << 16)
        status = CGMStatusFlags(status_raw)

        _min_length_with_crc = 7
        e2e_crc: int | None = None
        if len(data) >= _min_length_with_crc:
            e2e_crc = DataParser.parse_int16(data, 5, signed=False)

        return CGMStatusData(
            time_offset=time_offset,
            status=status,
            e2e_crc=e2e_crc,
        )

    def _encode_value(self, data: CGMStatusData) -> bytearray:
        """Encode CGMStatusData back to BLE bytes.

        Args:
            data: CGMStatusData instance.

        Returns:
            Encoded bytearray (5 or 7 bytes).

        """
        result = DataParser.encode_int16(data.time_offset, signed=False)
        status_int = int(data.status)
        result.extend(
            bytearray(
                [
                    status_int & 0xFF,
                    (status_int >> 8) & 0xFF,
                    (status_int >> 16) & 0xFF,
                ]
            )
        )
        if data.e2e_crc is not None:
            result.extend(DataParser.encode_int16(data.e2e_crc, signed=False))
        return result
