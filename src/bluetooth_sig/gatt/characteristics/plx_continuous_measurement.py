"""PLX Continuous Measurement characteristic implementation."""

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


class PLXContinuousFlags(IntFlag):
    """PLX Continuous measurement flags (Table 3.7 PLXS v1.0.1)."""

    SPO2PR_FAST_PRESENT = 0x01  # Bit 0: SpO2PR-Fast field is present
    SPO2PR_SLOW_PRESENT = 0x02  # Bit 1: SpO2PR-Slow field is present
    MEASUREMENT_STATUS_PRESENT = 0x04  # Bit 2: Measurement Status field is present
    DEVICE_AND_SENSOR_STATUS_PRESENT = 0x08  # Bit 3: Device and Sensor Status field is present
    PULSE_AMPLITUDE_INDEX_PRESENT = 0x10  # Bit 4: Pulse Amplitude Index field is present


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


class PLXContinuousData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed PLX continuous measurement data (Table 3.6 PLXS v1.0.1)."""

    continuous_flags: PLXContinuousFlags
    spo2: float  # SpO2PR-Normal SpO2 (mandatory)
    pulse_rate: float  # SpO2PR-Normal PR (mandatory)
    spo2_fast: float | None = None  # SpO2PR-Fast SpO2 (optional, bit 0)
    pulse_rate_fast: float | None = None  # SpO2PR-Fast PR (optional, bit 0)
    spo2_slow: float | None = None  # SpO2PR-Slow SpO2 (optional, bit 1)
    pulse_rate_slow: float | None = None  # SpO2PR-Slow PR (optional, bit 1)
    measurement_status: PLXMeasurementStatus | None = None
    device_and_sensor_status: PLXDeviceAndSensorStatus | None = None
    pulse_amplitude_index: float | None = None
    supported_features: PLXFeatureFlags | None = None


class PLXContinuousMeasurementCharacteristic(BaseCharacteristic[PLXContinuousData]):
    """PLX Continuous Measurement characteristic (0x2A5F).

    Used to transmit continuous SpO2 (blood oxygen saturation) and pulse rate
    measurements from pulse oximetry devices.

    Format (Table 3.6): Flags(1) + SpO2PR-Normal(4) + [SpO2PR-Fast(4)] +
    [SpO2PR-Slow(4)] + [Measurement Status(2)] + [Device and Sensor Status(3)] +
    [Pulse Amplitude Index(2)]
    """

    _characteristic_name: str = "PLX Continuous Measurement"

    _optional_dependencies: ClassVar[list[type[BaseCharacteristic[Any]]]] = [PLXFeaturesCharacteristic]

    # Declarative validation
    min_length: int | None = 5  # Flags(1) + SpO2(2) + PulseRate(2) minimum
    max_length: int | None = 20  # + Fast(4) + Slow(4) + MeasStatus(2) + DevSensStatus(3) + PAI(2)
    allow_variable_length: bool = True

    def _decode_value(  # pylint: disable=too-many-locals,too-many-branches
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> PLXContinuousData:
        """Parse PLX continuous measurement data per PLXS v1.0.1.

        Format (Table 3.6): Flags(1) + SpO2PR-Normal(4) + [SpO2PR-Fast(4)] +
        [SpO2PR-Slow(4)] + [Measurement Status(2)] + [Device and Sensor Status(3)] +
        [Pulse Amplitude Index(2)]
        All SpO2/PR fields are IEEE-11073 16-bit SFLOAT.
        """
        if validate and len(data) < 5:
            raise ValueError(f"Insufficient data for PLX continuous measurement: {len(data)} < 5")

        offset = 0

        # Parse flags
        continuous_flags = PLXContinuousFlags(data[offset])
        offset += 1

        # Parse SpO2PR-Normal (mandatory): SpO2 + PR — IEEE-11073 SFLOAT
        spo2 = IEEE11073Parser.parse_sfloat(data, offset)
        offset += 2

        pulse_rate = IEEE11073Parser.parse_sfloat(data, offset)
        offset += 2

        # Parse optional SpO2PR-Fast (4 bytes) — bit 0
        spo2_fast: float | None = None
        pulse_rate_fast: float | None = None
        if continuous_flags & PLXContinuousFlags.SPO2PR_FAST_PRESENT:
            if validate and offset + 4 > len(data):
                raise ValueError(f"Not enough data for SpO2PR-Fast: {len(data)} < {offset + 4}")
            spo2_fast = IEEE11073Parser.parse_sfloat(data, offset)
            offset += 2
            pulse_rate_fast = IEEE11073Parser.parse_sfloat(data, offset)
            offset += 2

        # Parse optional SpO2PR-Slow (4 bytes) — bit 1
        spo2_slow: float | None = None
        pulse_rate_slow: float | None = None
        if continuous_flags & PLXContinuousFlags.SPO2PR_SLOW_PRESENT:
            if validate and offset + 4 > len(data):
                raise ValueError(f"Not enough data for SpO2PR-Slow: {len(data)} < {offset + 4}")
            spo2_slow = IEEE11073Parser.parse_sfloat(data, offset)
            offset += 2
            pulse_rate_slow = IEEE11073Parser.parse_sfloat(data, offset)
            offset += 2

        # Parse optional Measurement Status (2 bytes) — bit 2
        measurement_status = None
        if continuous_flags & PLXContinuousFlags.MEASUREMENT_STATUS_PRESENT:
            if validate and offset + 2 > len(data):
                raise ValueError(f"Not enough data for measurement status: {len(data)} < {offset + 2}")
            measurement_status = PLXMeasurementStatus(DataParser.parse_int16(data, offset, signed=False))
            offset += 2

        # Parse optional Device and Sensor Status (3 bytes) — bit 3
        device_and_sensor_status = None
        if continuous_flags & PLXContinuousFlags.DEVICE_AND_SENSOR_STATUS_PRESENT:
            if validate and offset + 3 > len(data):
                raise ValueError(f"Not enough data for device/sensor status: {len(data)} < {offset + 3}")
            device_and_sensor_status = PLXDeviceAndSensorStatus(
                DataParser.parse_int32(data[offset : offset + 3] + b"\x00", 0, signed=False)
            )
            offset += 3

        # Parse optional Pulse Amplitude Index (2 bytes) — bit 4
        pulse_amplitude_index = None
        if continuous_flags & PLXContinuousFlags.PULSE_AMPLITUDE_INDEX_PRESENT:
            if validate and offset + 2 > len(data):
                raise ValueError(f"Not enough data for pulse amplitude index: {len(data)} < {offset + 2}")
            pulse_amplitude_index = IEEE11073Parser.parse_sfloat(data, offset)
            offset += 2

        # Context enhancement: PLX Features
        supported_features: PLXFeatureFlags | None = None
        if ctx:
            plx_features_value = self.get_context_characteristic(ctx, CharacteristicName.PLX_FEATURES)
            if plx_features_value is not None:
                supported_features = plx_features_value

        return PLXContinuousData(
            continuous_flags=continuous_flags,
            spo2=spo2,
            pulse_rate=pulse_rate,
            spo2_fast=spo2_fast,
            pulse_rate_fast=pulse_rate_fast,
            spo2_slow=spo2_slow,
            pulse_rate_slow=pulse_rate_slow,
            measurement_status=measurement_status,
            device_and_sensor_status=device_and_sensor_status,
            pulse_amplitude_index=pulse_amplitude_index,
            supported_features=supported_features,
        )

    def _encode_value(self, data: PLXContinuousData) -> bytearray:
        """Encode PLX continuous measurement data."""
        result = bytearray()

        # Encode flags
        result.append(int(data.continuous_flags))

        # Encode SpO2PR-Normal (mandatory): SpO2 + PR
        result.extend(IEEE11073Parser.encode_sfloat(data.spo2))
        result.extend(IEEE11073Parser.encode_sfloat(data.pulse_rate))

        # Encode optional SpO2PR-Fast
        if data.continuous_flags & PLXContinuousFlags.SPO2PR_FAST_PRESENT:
            if data.spo2_fast is None or data.pulse_rate_fast is None:
                raise ValueError("SpO2PR-Fast flag set but values are None")
            result.extend(IEEE11073Parser.encode_sfloat(data.spo2_fast))
            result.extend(IEEE11073Parser.encode_sfloat(data.pulse_rate_fast))

        # Encode optional SpO2PR-Slow
        if data.continuous_flags & PLXContinuousFlags.SPO2PR_SLOW_PRESENT:
            if data.spo2_slow is None or data.pulse_rate_slow is None:
                raise ValueError("SpO2PR-Slow flag set but values are None")
            result.extend(IEEE11073Parser.encode_sfloat(data.spo2_slow))
            result.extend(IEEE11073Parser.encode_sfloat(data.pulse_rate_slow))

        # Encode optional Measurement Status
        if data.continuous_flags & PLXContinuousFlags.MEASUREMENT_STATUS_PRESENT:
            if data.measurement_status is None:
                raise ValueError("Measurement Status flag set but value is None")
            result.extend(int(data.measurement_status).to_bytes(2, byteorder="little", signed=False))

        # Encode optional Device and Sensor Status
        if data.continuous_flags & PLXContinuousFlags.DEVICE_AND_SENSOR_STATUS_PRESENT:
            if data.device_and_sensor_status is None:
                raise ValueError("Device/Sensor Status flag set but value is None")
            status_val = int(data.device_and_sensor_status)
            result.append(status_val & 0xFF)
            result.append((status_val >> 8) & 0xFF)
            result.append((status_val >> 16) & 0xFF)

        # Encode optional Pulse Amplitude Index
        if data.continuous_flags & PLXContinuousFlags.PULSE_AMPLITUDE_INDEX_PRESENT:
            if data.pulse_amplitude_index is None:
                raise ValueError("Pulse Amplitude Index flag set but value is None")
            result.extend(IEEE11073Parser.encode_sfloat(data.pulse_amplitude_index))

        return result
