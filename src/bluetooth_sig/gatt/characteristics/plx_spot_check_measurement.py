"""PLX Spot-Check Measurement characteristic implementation."""

from __future__ import annotations

import logging
from datetime import datetime
from enum import IntFlag
from typing import Any, ClassVar

import msgspec

from ...types.gatt_enums import CharacteristicName
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .plx_features import PLXFeatureFlags, PLXFeaturesCharacteristic
from .utils import DataParser, IEEE11073Parser

logger = logging.getLogger(__name__)


class PLXSpotCheckFlags(IntFlag):
    """PLX Spot-Check measurement flags (Table 3.3 PLXS v1.0.1)."""

    TIMESTAMP_PRESENT = 0x01  # Bit 0: Timestamp field is present
    MEASUREMENT_STATUS_PRESENT = 0x02  # Bit 1: Measurement Status field is present
    DEVICE_AND_SENSOR_STATUS_PRESENT = 0x04  # Bit 2: Device and Sensor Status field is present
    PULSE_AMPLITUDE_INDEX_PRESENT = 0x08  # Bit 3: Pulse Amplitude Index field is present
    DEVICE_CLOCK_NOT_SET = 0x10  # Bit 4: Device Clock is Not Set


class PLXMeasurementStatus(IntFlag):
    """PLX Measurement Status flags (16-bit, Table 3.4 PLXS v1.0.1).

    Bits 0-4 are RFU. Status bits start at bit 5.
    """

    MEASUREMENT_ONGOING = 0x0020  # Bit 5
    EARLY_ESTIMATED_DATA = 0x0040  # Bit 6
    VALIDATED_DATA = 0x0080  # Bit 7
    FULLY_QUALIFIED_DATA = 0x0100  # Bit 8
    DATA_FROM_MEASUREMENT_STORAGE = 0x0200  # Bit 9
    DATA_FOR_DEMONSTRATION = 0x0400  # Bit 10
    DATA_FOR_TESTING = 0x0800  # Bit 11
    CALIBRATION_ONGOING = 0x1000  # Bit 12
    MEASUREMENT_UNAVAILABLE = 0x2000  # Bit 13
    QUESTIONABLE_MEASUREMENT_DETECTED = 0x4000  # Bit 14
    INVALID_MEASUREMENT_DETECTED = 0x8000  # Bit 15


class PLXDeviceAndSensorStatus(IntFlag):
    """PLX Device and Sensor Status flags (24-bit, Table 3.5 PLXS v1.0.1)."""

    EXTENDED_DISPLAY_UPDATE_ONGOING = 0x000001  # Bit 0
    EQUIPMENT_MALFUNCTION_DETECTED = 0x000002  # Bit 1
    SIGNAL_PROCESSING_IRREGULARITY = 0x000004  # Bit 2
    INADEQUATE_SIGNAL_DETECTED = 0x000008  # Bit 3
    POOR_SIGNAL_DETECTED = 0x000010  # Bit 4
    LOW_PERFUSION_DETECTED = 0x000020  # Bit 5
    ERRATIC_SIGNAL_DETECTED = 0x000040  # Bit 6
    NON_PULSATILE_SIGNAL_DETECTED = 0x000080  # Bit 7
    QUESTIONABLE_PULSE_DETECTED = 0x000100  # Bit 8
    SIGNAL_ANALYSIS_ONGOING = 0x000200  # Bit 9
    SENSOR_INTERFERENCE_DETECTED = 0x000400  # Bit 10
    SENSOR_UNCONNECTED_TO_USER = 0x000800  # Bit 11
    UNKNOWN_SENSOR_CONNECTED = 0x001000  # Bit 12
    SENSOR_DISPLACED = 0x002000  # Bit 13
    SENSOR_MALFUNCTIONING = 0x004000  # Bit 14
    SENSOR_DISCONNECTED = 0x008000  # Bit 15


class PLXSpotCheckData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed PLX spot-check measurement data (Table 3.2 PLXS v1.0.1)."""

    spot_check_flags: PLXSpotCheckFlags  # PLX spot-check measurement flags
    spo2: float  # Blood oxygen saturation percentage (SpO2) — SFLOAT
    pulse_rate: float  # Pulse rate in beats per minute — SFLOAT
    timestamp: datetime | None = None  # Optional DateTime (7 octets) per Table 3.3 bit 0
    measurement_status: PLXMeasurementStatus | None = None  # Optional measurement status flags (16-bit)
    device_and_sensor_status: PLXDeviceAndSensorStatus | None = None  # Optional device/sensor status (24-bit)
    pulse_amplitude_index: float | None = None  # Optional pulse amplitude index (SFLOAT, %)
    supported_features: PLXFeatureFlags | None = None  # Optional PLX features from context


class PLXSpotCheckMeasurementCharacteristic(BaseCharacteristic[PLXSpotCheckData]):
    """PLX Spot-Check Measurement characteristic (0x2A5E).

    Used to transmit single SpO2 (blood oxygen saturation) and pulse rate
    measurements from spot-check readings.
    """

    _characteristic_name: str = "PLX Spot-Check Measurement"

    _optional_dependencies: ClassVar[list[type[BaseCharacteristic[Any]]]] = [PLXFeaturesCharacteristic]

    # Declarative validation (automatic)
    min_length: int | None = 5  # Flags(1) + SpO2(2) + PulseRate(2) minimum
    max_length: int | None = (
        19  # + Timestamp(7) + MeasurementStatus(2) + DeviceAndSensorStatus(3) + PulseAmplitudeIndex(2)
    )
    allow_variable_length: bool = True  # Variable optional fields

    def _decode_value(  # pylint: disable=too-many-locals,too-many-branches  # Complexity needed for spec parsing
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> PLXSpotCheckData:
        """Parse PLX spot-check measurement data per PLXS v1.0.1.

        Format (Table 3.2): Flags(1) + SpO2(2) + PR(2) + [Timestamp(7)] +
        [Measurement Status(2)] + [Device and Sensor Status(3)] + [Pulse Amplitude Index(2)]
        SpO2 and Pulse Rate are IEEE-11073 16-bit SFLOAT.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).
            validate: Whether to validate ranges (default True)

        Returns:
            PLXSpotCheckData containing parsed PLX spot-check data.

        """
        flags = PLXSpotCheckFlags(data[0])

        # Parse SpO2 and pulse rate using IEEE-11073 SFLOAT format
        spo2 = IEEE11073Parser.parse_sfloat(data, 1)
        pulse_rate = IEEE11073Parser.parse_sfloat(data, 3)

        # Parse optional fields in order per Table 3.2
        timestamp: datetime | None = None
        measurement_status: PLXMeasurementStatus | None = None
        device_and_sensor_status: PLXDeviceAndSensorStatus | None = None
        pulse_amplitude_index: float | None = None
        offset = 5

        # Timestamp (7 octets DateTime) — Table 3.3 bit 0
        if PLXSpotCheckFlags.TIMESTAMP_PRESENT in flags and len(data) >= offset + 7:
            timestamp = IEEE11073Parser.parse_timestamp(data, offset)
            offset += 7

        if PLXSpotCheckFlags.MEASUREMENT_STATUS_PRESENT in flags and len(data) >= offset + 2:
            measurement_status = PLXMeasurementStatus(DataParser.parse_int16(data, offset, signed=False))
            offset += 2

        if PLXSpotCheckFlags.DEVICE_AND_SENSOR_STATUS_PRESENT in flags and len(data) >= offset + 3:
            device_and_sensor_status = PLXDeviceAndSensorStatus(
                DataParser.parse_int32(data[offset : offset + 3] + b"\x00", 0, signed=False)
            )  # Pad to 4 bytes
            offset += 3

        if PLXSpotCheckFlags.PULSE_AMPLITUDE_INDEX_PRESENT in flags and len(data) >= offset + 2:
            pulse_amplitude_index = IEEE11073Parser.parse_sfloat(data, offset)

        # Context enhancement: PLX Features
        supported_features: PLXFeatureFlags | None = None
        if ctx:
            plx_features_value = self.get_context_characteristic(ctx, CharacteristicName.PLX_FEATURES)
            if plx_features_value is not None:
                supported_features = plx_features_value

        return PLXSpotCheckData(
            spot_check_flags=flags,
            spo2=spo2,
            pulse_rate=pulse_rate,
            timestamp=timestamp,
            measurement_status=measurement_status,
            device_and_sensor_status=device_and_sensor_status,
            pulse_amplitude_index=pulse_amplitude_index,
            supported_features=supported_features,
        )

    def _encode_value(self, data: PLXSpotCheckData) -> bytearray:
        """Encode PLX spot-check measurement value back to bytes.

        Args:
            data: PLXSpotCheckData instance to encode

        Returns:
            Encoded bytes representing the measurement

        """
        # Build flags
        flags = data.spot_check_flags

        # Build result
        result = bytearray([int(flags)])
        result.extend(IEEE11073Parser.encode_sfloat(data.spo2))
        result.extend(IEEE11073Parser.encode_sfloat(data.pulse_rate))

        # Encode optional timestamp (7 bytes DateTime)
        if data.timestamp is not None:
            result.extend(IEEE11073Parser.encode_timestamp(data.timestamp))

        # Encode optional measurement status
        if data.measurement_status is not None:
            result.extend(DataParser.encode_int16(int(data.measurement_status), signed=False))

        # Encode optional device and sensor status
        if data.device_and_sensor_status is not None:
            # Device and sensor status is 3 bytes (24-bit value)
            device_status_bytes = DataParser.encode_int32(int(data.device_and_sensor_status), signed=False)[:3]
            result.extend(device_status_bytes)

        # Encode optional pulse amplitude index
        if data.pulse_amplitude_index is not None:
            result.extend(IEEE11073Parser.encode_sfloat(data.pulse_amplitude_index))

        return result
