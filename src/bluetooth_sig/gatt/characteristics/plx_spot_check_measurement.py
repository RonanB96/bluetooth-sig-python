"""PLX Spot-Check Measurement characteristic implementation."""

from __future__ import annotations

import logging
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
    """PLX Spot-Check measurement flags."""

    SPO2PR_FAST = 0x01
    MEASUREMENT_STATUS_PRESENT = 0x02
    DEVICE_AND_SENSOR_STATUS_PRESENT = 0x04
    PULSE_AMPLITUDE_INDEX_PRESENT = 0x08


class PLXMeasurementStatus(IntFlag):
    """PLX Measurement Status flags (16-bit)."""

    MEASUREMENT_ONGOING = 0x0001
    EARLY_ESTIMATED_DATA = 0x0002
    VALIDATED_DATA = 0x0004
    FULLY_QUALIFIED_DATA = 0x0008
    DATA_FROM_MEASUREMENT_STORAGE = 0x0010
    DATA_FOR_DEMONSTRATION = 0x0020
    DATA_FROM_TESTING_SIMULATION = 0x0040
    DATA_FROM_CALIBRATION_TEST = 0x0080


class PLXDeviceAndSensorStatus(IntFlag):
    """PLX Device and Sensor Status flags (24-bit)."""

    # Device Status (bits 0-15, same as Measurement Status)
    DEVICE_MEASUREMENT_ONGOING = 0x000001
    DEVICE_EARLY_ESTIMATED_DATA = 0x000002
    DEVICE_VALIDATED_DATA = 0x000004
    DEVICE_FULLY_QUALIFIED_DATA = 0x000008
    DEVICE_DATA_FROM_MEASUREMENT_STORAGE = 0x000010
    DEVICE_DATA_FOR_DEMONSTRATION = 0x000020
    DEVICE_DATA_FROM_TESTING_SIMULATION = 0x000040
    DEVICE_DATA_FROM_CALIBRATION_TEST = 0x000080

    # Sensor Status (bits 16-23)
    SENSOR_OPERATIONAL = 0x000100
    SENSOR_DEFECTIVE = 0x000200
    SENSOR_DISCONNECTED = 0x000400
    SENSOR_MALFUNCTIONING = 0x000800
    SENSOR_UNCALIBRATED = 0x001000
    SENSOR_NOT_OPERATIONAL = 0x002000


class PLXSpotCheckData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed PLX spot-check measurement data."""

    spot_check_flags: PLXSpotCheckFlags  # PLX spot-check measurement flags
    spo2: float  # Blood oxygen saturation percentage (SpO2)
    pulse_rate: float  # Pulse rate in beats per minute
    measurement_status: PLXMeasurementStatus | None = None  # Optional measurement status flags
    device_and_sensor_status: PLXDeviceAndSensorStatus | None = None  # Optional device and sensor status flags
    pulse_amplitude_index: float | None = None  # Optional pulse amplitude index value
    supported_features: PLXFeatureFlags | None = None  # Optional PLX features from context (PLXFeatureFlags enum)


class PLXSpotCheckMeasurementCharacteristic(BaseCharacteristic[PLXSpotCheckData]):
    """PLX Spot-Check Measurement characteristic (0x2A5E).

    Used to transmit single SpO2 (blood oxygen saturation) and pulse rate
    measurements from spot-check readings.
    """

    _python_type: type | str | None = dict

    _characteristic_name: str = "PLX Spot-Check Measurement"

    _optional_dependencies: ClassVar[list[type[BaseCharacteristic[Any]]]] = [PLXFeaturesCharacteristic]

    # Declarative validation (automatic)
    min_length: int | None = 5  # Flags(1) + SpO2(2) + PulseRate(2) minimum
    max_length: int | None = 12  # + MeasurementStatus(2) + DeviceAndSensorStatus(3) + PulseAmplitudeIndex(2) maximum
    allow_variable_length: bool = True  # Variable optional fields

    def _decode_value(  # pylint: disable=too-many-locals,too-many-branches  # Complexity needed for spec parsing
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> PLXSpotCheckData:
        """Parse PLX spot-check measurement data according to Bluetooth specification.

        Format: Flags(1) + SpO2(2) + Pulse Rate(2) + [Measurement Status(2)] +
        [Device and Sensor Status(3)] + [Pulse Amplitude Index(2)]
        SpO2 and Pulse Rate are IEEE-11073 16-bit SFLOAT.

        Context Enhancement:
            If ctx is provided, this method will attempt to enhance the parsed data with:
            - PLX Features (0x2A60): Device capabilities and supported measurement types

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).
            validate: Whether to validate ranges (default True)

        Returns:
            PLXSpotCheckData containing parsed PLX spot-check data with optional
            context-enhanced information.

        """
        flags = PLXSpotCheckFlags(data[0])

        # Parse SpO2 and pulse rate using IEEE-11073 SFLOAT format
        spo2 = IEEE11073Parser.parse_sfloat(data, 1)
        pulse_rate = IEEE11073Parser.parse_sfloat(data, 3)

        # Parse optional fields
        measurement_status: PLXMeasurementStatus | None = None
        device_and_sensor_status: PLXDeviceAndSensorStatus | None = None
        pulse_amplitude_index: float | None = None
        offset = 5

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
                # PLX Features returns PLXFeatureFlags enum
                supported_features = plx_features_value

        # Create immutable struct with all values
        return PLXSpotCheckData(
            spot_check_flags=flags,
            spo2=spo2,
            pulse_rate=pulse_rate,
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
