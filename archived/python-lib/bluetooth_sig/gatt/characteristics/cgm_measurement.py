"""CGM Measurement characteristic implementation.

Implements the CGM Measurement characteristic (0x2AA7).  The characteristic
value contains one or more CGM Measurement Records concatenated together.

Each record contains:
    Size (uint8) -- total size of the record including this field
    Flags (uint8) -- controls presence of optional fields
    CGM Glucose Concentration (medfloat16)
    Time Offset (uint16) -- minutes since session start
    Sensor Status Annunciation (0-3 octets, flag-gated)
    CGM Trend Information (medfloat16, optional)
    CGM Quality (medfloat16, optional)

Flag-bit assignments:
    Bit 0: CGM Trend Information present
    Bit 1: CGM Quality present
    Bits 2-4: Reserved
    Bit 5: Warning-Octet present (Sensor Status Annunciation)
    Bit 6: Cal/Temp-Octet present (Sensor Status Annunciation)
    Bit 7: Status-Octet present (Sensor Status Annunciation)

References:
    Bluetooth SIG Continuous Glucose Monitoring Service
    org.bluetooth.characteristic.cgm_measurement (GSS YAML)
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser


class CGMMeasurementFlags(IntFlag):
    """CGM Measurement record flags."""

    TREND_INFORMATION_PRESENT = 0x01
    QUALITY_PRESENT = 0x02
    WARNING_OCTET_PRESENT = 0x20
    CAL_TEMP_OCTET_PRESENT = 0x40
    STATUS_OCTET_PRESENT = 0x80


class CGMSensorStatusOctet(IntFlag):
    """CGM Sensor Status Annunciation — Status octet (bits 0-7)."""

    SESSION_STOPPED = 0x01
    DEVICE_BATTERY_LOW = 0x02
    SENSOR_TYPE_INCORRECT = 0x04
    SENSOR_MALFUNCTION = 0x08
    DEVICE_SPECIFIC_ALERT = 0x10
    GENERAL_DEVICE_FAULT = 0x20


class CGMCalTempOctet(IntFlag):
    """CGM Sensor Status Annunciation — Cal/Temp octet (bits 8-15)."""

    TIME_SYNC_REQUIRED = 0x01
    CALIBRATION_NOT_ALLOWED = 0x02
    CALIBRATION_RECOMMENDED = 0x04
    CALIBRATION_REQUIRED = 0x08
    SENSOR_TEMP_TOO_HIGH = 0x10
    SENSOR_TEMP_TOO_LOW = 0x20
    CALIBRATION_PENDING = 0x40


class CGMWarningOctet(IntFlag):
    """CGM Sensor Status Annunciation — Warning octet (bits 16-23)."""

    RESULT_LOWER_THAN_PATIENT_LOW = 0x01
    RESULT_HIGHER_THAN_PATIENT_HIGH = 0x02
    RESULT_LOWER_THAN_HYPO = 0x04
    RESULT_HIGHER_THAN_HYPER = 0x08
    RATE_OF_DECREASE_EXCEEDED = 0x10
    RATE_OF_INCREASE_EXCEEDED = 0x20
    RESULT_LOWER_THAN_DEVICE_CAN_PROCESS = 0x40
    RESULT_HIGHER_THAN_DEVICE_CAN_PROCESS = 0x80


class CGMMeasurementRecord(msgspec.Struct, frozen=True, kw_only=True):
    """A single CGM Measurement Record.

    Attributes:
        size: Total size of this record in bytes (including the size field).
        flags: Raw 8-bit flags field.
        glucose_concentration: Glucose concentration in mg/dL.
        time_offset: Minutes since session start.
        status_octet: Sensor status octet (8 bits). None if absent.
        cal_temp_octet: Calibration/temperature octet (8 bits). None if absent.
        warning_octet: Warning octet (8 bits). None if absent.
        trend_information: Glucose trend rate (mg/dL/min). None if absent.
        quality: CGM quality percentage. None if absent.

    """

    size: int
    flags: CGMMeasurementFlags
    glucose_concentration: float
    time_offset: int
    status_octet: CGMSensorStatusOctet | None = None
    cal_temp_octet: CGMCalTempOctet | None = None
    warning_octet: CGMWarningOctet | None = None
    trend_information: float | None = None
    quality: float | None = None


class CGMMeasurementData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from CGM Measurement characteristic.

    Attributes:
        records: List of CGM Measurement Records.

    """

    records: tuple[CGMMeasurementRecord, ...]


def _decode_single_record(data: bytearray, start: int) -> tuple[CGMMeasurementRecord, int]:
    """Decode a single CGM Measurement Record from data at the given offset.

    Args:
        data: Full characteristic data.
        start: Byte offset where this record begins.

    Returns:
        Tuple of (decoded record, next offset after this record).

    """
    record_size = data[start]
    flags = CGMMeasurementFlags(data[start + 1])
    glucose_concentration = IEEE11073Parser.parse_sfloat(data, start + 2)
    time_offset = DataParser.parse_int16(data, start + 4, signed=False)
    offset = start + 6

    # Sensor Status Annunciation: order is Status, Cal/Temp, Warning
    # (per YAML spec structure order)
    status_octet: CGMSensorStatusOctet | None = None
    if flags & CGMMeasurementFlags.STATUS_OCTET_PRESENT:
        status_octet = CGMSensorStatusOctet(data[offset])
        offset += 1

    cal_temp_octet: CGMCalTempOctet | None = None
    if flags & CGMMeasurementFlags.CAL_TEMP_OCTET_PRESENT:
        cal_temp_octet = CGMCalTempOctet(data[offset])
        offset += 1

    warning_octet: CGMWarningOctet | None = None
    if flags & CGMMeasurementFlags.WARNING_OCTET_PRESENT:
        warning_octet = CGMWarningOctet(data[offset])
        offset += 1

    trend_information: float | None = None
    if flags & CGMMeasurementFlags.TREND_INFORMATION_PRESENT:
        trend_information = IEEE11073Parser.parse_sfloat(data, offset)
        offset += 2

    quality: float | None = None
    if flags & CGMMeasurementFlags.QUALITY_PRESENT:
        quality = IEEE11073Parser.parse_sfloat(data, offset)
        offset += 2

    # Skip any remaining bytes in this record (e.g. E2E-CRC)
    record_end = start + record_size
    return (
        CGMMeasurementRecord(
            size=record_size,
            flags=flags,
            glucose_concentration=glucose_concentration,
            time_offset=time_offset,
            status_octet=status_octet,
            cal_temp_octet=cal_temp_octet,
            warning_octet=warning_octet,
            trend_information=trend_information,
            quality=quality,
        ),
        record_end,
    )


def _encode_single_record(record: CGMMeasurementRecord) -> bytearray:
    """Encode a single CGM Measurement Record to bytes.

    Args:
        record: CGMMeasurementRecord instance.

    Returns:
        Encoded bytearray for this record.

    """
    flags = CGMMeasurementFlags(0)
    if record.trend_information is not None:
        flags |= CGMMeasurementFlags.TREND_INFORMATION_PRESENT
    if record.quality is not None:
        flags |= CGMMeasurementFlags.QUALITY_PRESENT
    if record.status_octet is not None:
        flags |= CGMMeasurementFlags.STATUS_OCTET_PRESENT
    if record.cal_temp_octet is not None:
        flags |= CGMMeasurementFlags.CAL_TEMP_OCTET_PRESENT
    if record.warning_octet is not None:
        flags |= CGMMeasurementFlags.WARNING_OCTET_PRESENT

    body = bytearray()
    # Placeholder for size byte — filled in at the end
    body.append(0)
    body.append(int(flags))
    body.extend(IEEE11073Parser.encode_sfloat(record.glucose_concentration))
    body.extend(DataParser.encode_int16(record.time_offset, signed=False))

    if record.status_octet is not None:
        body.append(int(record.status_octet))
    if record.cal_temp_octet is not None:
        body.append(int(record.cal_temp_octet))
    if record.warning_octet is not None:
        body.append(int(record.warning_octet))
    if record.trend_information is not None:
        body.extend(IEEE11073Parser.encode_sfloat(record.trend_information))
    if record.quality is not None:
        body.extend(IEEE11073Parser.encode_sfloat(record.quality))

    body[0] = len(body)
    return body


class CGMMeasurementCharacteristic(BaseCharacteristic[CGMMeasurementData]):
    """CGM Measurement characteristic (0x2AA7).

    Contains one or more CGM Measurement Records concatenated together.
    Each record is self-sized via its leading Size byte.
    """

    expected_type = CGMMeasurementData
    min_length: int = 6  # At least one record: size(1)+flags(1)+glucose(2)+time(2)
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> CGMMeasurementData:
        """Parse CGM Measurement records from raw BLE bytes.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            CGMMeasurementData containing all parsed records.

        """
        records: list[CGMMeasurementRecord] = []
        offset = 0
        while offset < len(data):
            record, offset = _decode_single_record(data, offset)
            records.append(record)

        return CGMMeasurementData(records=tuple(records))

    def _encode_value(self, data: CGMMeasurementData) -> bytearray:
        """Encode CGMMeasurementData back to BLE bytes.

        Args:
            data: CGMMeasurementData instance.

        Returns:
            Encoded bytearray with all records concatenated.

        """
        result = bytearray()
        for record in data.records:
            result.extend(_encode_single_record(record))
        return result
