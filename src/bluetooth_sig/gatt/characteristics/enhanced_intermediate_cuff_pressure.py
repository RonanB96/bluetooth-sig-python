"""Enhanced Intermediate Cuff Pressure characteristic implementation.

Implements the Enhanced Intermediate Cuff Pressure characteristic (0x2B35).
Reports a single intermediate cuff pressure reading (medfloat16) during
an ongoing measurement, with enhanced optional fields matching the Enhanced
Blood Pressure Measurement pattern.

Flag-bit assignments (from GSS YAML):
    Bit 0: Units (0=mmHg, 1=kPa)
    Bit 1: Time Stamp present (uint32 seconds since epoch)
    Bit 2: Pulse Rate present (medfloat16)
    Bit 3: User ID present (uint8)
    Bit 4: Measurement Status present (boolean[16])
    Bit 5: User Facing Time present (uint32 seconds since epoch)
    Bit 6: Epoch Start 2000 (0=1900, 1=2000)
    Bit 7: Reserved

References:
    Bluetooth SIG Blood Pressure Service 1.1
    org.bluetooth.characteristic.enhanced_intermediate_cuff_pressure (GSS YAML)
"""

from __future__ import annotations

import msgspec

from bluetooth_sig.types.units import PressureUnit

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .blood_pressure_measurement import BloodPressureMeasurementStatus
from .enhanced_blood_pressure_measurement import EnhancedBloodPressureFlags, EpochYear
from .utils import DataParser, IEEE11073Parser


class EnhancedIntermediateCuffPressureData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Enhanced Intermediate Cuff Pressure characteristic.

    Attributes:
        flags: Raw 8-bit flags field.
        cuff_pressure: Current intermediate cuff pressure value.
        unit: Pressure unit (mmHg or kPa).
        timestamp: Seconds since epoch start. None if absent.
        pulse_rate: Pulse rate in BPM. None if absent.
        user_id: User ID (0-255). None if absent.
        measurement_status: 16-bit measurement status flags. None if absent.
        user_facing_time: User-facing time in seconds since epoch. None if absent.
        epoch_year: Epoch start year (1900 or 2000).

    """

    flags: EnhancedBloodPressureFlags
    cuff_pressure: float
    unit: PressureUnit
    timestamp: int | None = None
    pulse_rate: float | None = None
    user_id: int | None = None
    measurement_status: BloodPressureMeasurementStatus | None = None
    user_facing_time: int | None = None
    epoch_year: EpochYear = EpochYear.EPOCH_1900


class EnhancedIntermediateCuffPressureCharacteristic(
    BaseCharacteristic[EnhancedIntermediateCuffPressureData],
):
    """Enhanced Intermediate Cuff Pressure characteristic (0x2B35).

    Reports a single intermediate cuff pressure reading during an ongoing
    blood pressure measurement, with enhanced timestamps and epoch flag.
    """

    expected_type = EnhancedIntermediateCuffPressureData
    min_length: int = 3  # flags(1) + cuff_pressure(2)
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> EnhancedIntermediateCuffPressureData:
        """Parse Enhanced Intermediate Cuff Pressure from raw BLE bytes.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            EnhancedIntermediateCuffPressureData with all present fields.

        """
        flags = EnhancedBloodPressureFlags(data[0])
        unit = PressureUnit.KPA if flags & EnhancedBloodPressureFlags.UNITS_KPA else PressureUnit.MMHG

        # Mandatory single cuff pressure value (medfloat16)
        cuff_pressure = IEEE11073Parser.parse_sfloat(data, 1)
        offset = 3

        epoch_year = (
            EpochYear.EPOCH_2000 if flags & EnhancedBloodPressureFlags.EPOCH_START_2000 else EpochYear.EPOCH_1900
        )

        timestamp: int | None = None
        if flags & EnhancedBloodPressureFlags.TIMESTAMP_PRESENT:
            timestamp = DataParser.parse_int32(data, offset, signed=False)
            offset += 4

        pulse_rate: float | None = None
        if flags & EnhancedBloodPressureFlags.PULSE_RATE_PRESENT:
            pulse_rate = IEEE11073Parser.parse_sfloat(data, offset)
            offset += 2

        user_id: int | None = None
        if flags & EnhancedBloodPressureFlags.USER_ID_PRESENT:
            user_id = data[offset]
            offset += 1

        measurement_status: BloodPressureMeasurementStatus | None = None
        if flags & EnhancedBloodPressureFlags.MEASUREMENT_STATUS_PRESENT:
            measurement_status = BloodPressureMeasurementStatus(DataParser.parse_int16(data, offset, signed=False))
            offset += 2

        user_facing_time: int | None = None
        if flags & EnhancedBloodPressureFlags.USER_FACING_TIME_PRESENT:
            user_facing_time = DataParser.parse_int32(data, offset, signed=False)
            offset += 4

        return EnhancedIntermediateCuffPressureData(
            flags=flags,
            cuff_pressure=cuff_pressure,
            unit=unit,
            timestamp=timestamp,
            pulse_rate=pulse_rate,
            user_id=user_id,
            measurement_status=measurement_status,
            user_facing_time=user_facing_time,
            epoch_year=epoch_year,
        )

    def _encode_value(self, data: EnhancedIntermediateCuffPressureData) -> bytearray:
        """Encode EnhancedIntermediateCuffPressureData back to BLE bytes.

        Args:
            data: EnhancedIntermediateCuffPressureData instance.

        Returns:
            Encoded bytearray matching the BLE wire format.

        """
        flags = EnhancedBloodPressureFlags(0)
        if data.unit == PressureUnit.KPA:
            flags |= EnhancedBloodPressureFlags.UNITS_KPA
        if data.timestamp is not None:
            flags |= EnhancedBloodPressureFlags.TIMESTAMP_PRESENT
        if data.pulse_rate is not None:
            flags |= EnhancedBloodPressureFlags.PULSE_RATE_PRESENT
        if data.user_id is not None:
            flags |= EnhancedBloodPressureFlags.USER_ID_PRESENT
        if data.measurement_status is not None:
            flags |= EnhancedBloodPressureFlags.MEASUREMENT_STATUS_PRESENT
        if data.user_facing_time is not None:
            flags |= EnhancedBloodPressureFlags.USER_FACING_TIME_PRESENT
        if data.epoch_year == EpochYear.EPOCH_2000:
            flags |= EnhancedBloodPressureFlags.EPOCH_START_2000

        result = bytearray([int(flags)])
        result.extend(IEEE11073Parser.encode_sfloat(data.cuff_pressure))

        if data.timestamp is not None:
            result.extend(DataParser.encode_int32(data.timestamp, signed=False))

        if data.pulse_rate is not None:
            result.extend(IEEE11073Parser.encode_sfloat(data.pulse_rate))

        if data.user_id is not None:
            result.append(data.user_id)

        if data.measurement_status is not None:
            result.extend(DataParser.encode_int16(int(data.measurement_status), signed=False))

        if data.user_facing_time is not None:
            result.extend(DataParser.encode_int32(data.user_facing_time, signed=False))

        return result
