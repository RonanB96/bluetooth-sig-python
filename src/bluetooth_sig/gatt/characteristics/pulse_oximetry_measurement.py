"""Pulse Oximetry Measurement characteristic implementation."""

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


class PulseOximetryFlags(IntFlag):
    """Pulse Oximetry measurement flags."""

    TIMESTAMP_PRESENT = 0x01
    MEASUREMENT_STATUS_PRESENT = 0x02
    DEVICE_STATUS_PRESENT = 0x04
    PULSE_AMPLITUDE_INDEX_PRESENT = 0x08


class PulseOximetryData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed pulse oximetry measurement data.

    Attributes:
        spo2: Blood oxygen saturation percentage (SpO2)
        pulse_rate: Pulse rate in beats per minute
        timestamp: Optional timestamp of the measurement
        measurement_status: Optional measurement status flags
        device_status: Optional device status flags
        pulse_amplitude_index: Optional pulse amplitude index value
        supported_features: Optional PLX features from context (PLXFeatureFlags enum)
    """

    spo2: float
    pulse_rate: float
    timestamp: datetime | None = None
    measurement_status: int | None = None
    device_status: int | None = None
    pulse_amplitude_index: float | None = None
    supported_features: PLXFeatureFlags | None = None  # PLX Features from context (0x2A60)


class PulseOximetryMeasurementCharacteristic(BaseCharacteristic[PulseOximetryData]):
    """PLX Continuous Measurement characteristic (0x2A5F).

    Used to transmit SpO2 (blood oxygen saturation) and pulse rate
    measurements.
    """

    _python_type: type | str | None = dict

    _characteristic_name: str = "PLX Continuous Measurement"

    _optional_dependencies: ClassVar[list[type[BaseCharacteristic[Any]]]] = [PLXFeaturesCharacteristic]

    # Declarative validation (automatic)
    min_length: int | None = 5  # Flags(1) + SpO2(2) + PulseRate(2) minimum
    max_length: int | None = 16  # + Timestamp(7) + MeasurementStatus(2) + DeviceStatus(3) maximum
    allow_variable_length: bool = True  # Variable optional fields

    def _decode_value(  # pylint: disable=too-many-locals,too-many-branches  # Complexity needed for spec parsing
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> PulseOximetryData:
        """Parse pulse oximetry measurement data according to Bluetooth specification.

        Format: Flags(1) + SpO2(2) + Pulse Rate(2) + [Timestamp(7)] +
        [Measurement Status(2)] + [Device Status(3)] + [Pulse Amplitude Index(2)]
        SpO2 and Pulse Rate are IEEE-11073 16-bit SFLOAT.

        Context Enhancement:
            If ctx is provided, this method will attempt to enhance the parsed data with:
            - PLX Features (0x2A60): Device capabilities and supported measurement types

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).
            validate: Whether to validate ranges (default True)

        Returns:
            PulseOximetryData containing parsed pulse oximetry data with optional
            context-enhanced information.

        """
        flags = PulseOximetryFlags(data[0])

        # Parse SpO2 and pulse rate using IEEE-11073 SFLOAT format
        spo2 = IEEE11073Parser.parse_sfloat(data, 1)
        pulse_rate = IEEE11073Parser.parse_sfloat(data, 3)

        # Parse optional fields
        timestamp: datetime | None = None
        measurement_status: int | None = None
        device_status: int | None = None
        pulse_amplitude_index: float | None = None
        offset = 5

        if PulseOximetryFlags.TIMESTAMP_PRESENT in flags and len(data) >= offset + 7:
            timestamp = IEEE11073Parser.parse_timestamp(data, offset)
            offset += 7

        if PulseOximetryFlags.MEASUREMENT_STATUS_PRESENT in flags and len(data) >= offset + 2:
            measurement_status = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        if PulseOximetryFlags.DEVICE_STATUS_PRESENT in flags and len(data) >= offset + 3:
            device_status = DataParser.parse_int32(
                data[offset : offset + 3] + b"\x00", 0, signed=False
            )  # Pad to 4 bytes
            offset += 3

        if PulseOximetryFlags.PULSE_AMPLITUDE_INDEX_PRESENT in flags and len(data) >= offset + 2:
            pulse_amplitude_index = IEEE11073Parser.parse_sfloat(data, offset)

        # Context enhancement: PLX Features
        supported_features: PLXFeatureFlags | None = None
        if ctx:
            plx_features_value = self.get_context_characteristic(ctx, CharacteristicName.PLX_FEATURES)
            if plx_features_value is not None:
                # PLX Features returns PLXFeatureFlags enum
                supported_features = plx_features_value

        # Create immutable struct with all values
        return PulseOximetryData(
            spo2=spo2,
            pulse_rate=pulse_rate,
            timestamp=timestamp,
            measurement_status=measurement_status,
            device_status=device_status,
            pulse_amplitude_index=pulse_amplitude_index,
            supported_features=supported_features,
        )

    def _encode_value(self, data: PulseOximetryData) -> bytearray:
        """Encode pulse oximetry measurement value back to bytes.

        Args:
            data: PulseOximetryData instance to encode

        Returns:
            Encoded bytes representing the measurement

        """
        # Build flags
        flags = PulseOximetryFlags(0)
        if data.timestamp is not None:
            flags |= PulseOximetryFlags.TIMESTAMP_PRESENT
        if data.measurement_status is not None:
            flags |= PulseOximetryFlags.MEASUREMENT_STATUS_PRESENT
        if data.device_status is not None:
            flags |= PulseOximetryFlags.DEVICE_STATUS_PRESENT
        if data.pulse_amplitude_index is not None:
            flags |= PulseOximetryFlags.PULSE_AMPLITUDE_INDEX_PRESENT

        # Build result
        result = bytearray([int(flags)])
        result.extend(IEEE11073Parser.encode_sfloat(data.spo2))
        result.extend(IEEE11073Parser.encode_sfloat(data.pulse_rate))

        # Encode optional timestamp
        if data.timestamp is not None:
            result.extend(IEEE11073Parser.encode_timestamp(data.timestamp))

        # Encode optional measurement status
        if data.measurement_status is not None:
            result.extend(DataParser.encode_int16(data.measurement_status, signed=False))

        # Encode optional device status
        if data.device_status is not None:
            # Device status is 3 bytes (24-bit value)
            device_status_bytes = DataParser.encode_int32(data.device_status, signed=False)[:3]
            result.extend(device_status_bytes)

        # Encode optional pulse amplitude index
        if data.pulse_amplitude_index is not None:
            result.extend(IEEE11073Parser.encode_sfloat(data.pulse_amplitude_index))

        return result
