"""CGM Feature characteristic implementation.

Implements the CGM Feature characteristic (0x2AA8).  Fixed-size structure of
6 bytes: 24-bit feature flags + packed nibble type/location + 16-bit E2E-CRC.

Structure (from GSS YAML):
    CGM Feature (3 bytes, boolean[24])
    CGM Type-Sample Location (1 byte, two 4-bit nibbles packed)
    E2E-CRC (2 bytes, uint16) -- always present per spec

References:
    Bluetooth SIG Continuous Glucose Monitoring Service
    org.bluetooth.characteristic.cgm_feature (GSS YAML)
"""

from __future__ import annotations

from enum import IntEnum, IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_NIBBLE_MASK = 0x0F
_NIBBLE_SHIFT = 4


class CGMFeatureFlags(IntFlag):
    """CGM Feature flags (24-bit)."""

    CALIBRATION_SUPPORTED = 0x000001
    PATIENT_HIGH_LOW_ALERTS = 0x000002
    HYPO_ALERTS = 0x000004
    HYPER_ALERTS = 0x000008
    RATE_ALERTS = 0x000010
    DEVICE_SPECIFIC_ALERT = 0x000020
    SENSOR_MALFUNCTION_DETECTION = 0x000040
    SENSOR_TEMP_HIGH_LOW_DETECTION = 0x000080
    SENSOR_RESULT_HIGH_LOW_DETECTION = 0x000100
    LOW_BATTERY_DETECTION = 0x000200
    SENSOR_TYPE_ERROR_DETECTION = 0x000400
    GENERAL_DEVICE_FAULT = 0x000800
    E2E_CRC_SUPPORTED = 0x001000
    MULTIPLE_BOND_SUPPORTED = 0x002000
    MULTIPLE_SESSIONS_SUPPORTED = 0x004000
    CGM_TREND_INFORMATION_SUPPORTED = 0x008000
    CGM_QUALITY_SUPPORTED = 0x010000


class CGMType(IntEnum):
    """CGM sample type (lower nibble)."""

    CAPILLARY_WHOLE_BLOOD = 0x1
    CAPILLARY_PLASMA = 0x2
    VENOUS_WHOLE_BLOOD = 0x3
    VENOUS_PLASMA = 0x4
    ARTERIAL_WHOLE_BLOOD = 0x5
    ARTERIAL_PLASMA = 0x6
    UNDETERMINED_WHOLE_BLOOD = 0x7
    UNDETERMINED_PLASMA = 0x8
    INTERSTITIAL_FLUID = 0x9
    CONTROL_SOLUTION = 0xA


class CGMSampleLocation(IntEnum):
    """CGM sample location (upper nibble)."""

    FINGER = 0x1
    ALTERNATE_SITE_TEST = 0x2
    EARLOBE = 0x3
    CONTROL_SOLUTION = 0x4
    SUBCUTANEOUS_TISSUE = 0x5
    NOT_AVAILABLE = 0xF


class CGMFeatureData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from CGM Feature characteristic.

    Attributes:
        features: 24-bit CGM feature flags.
        cgm_type: CGM sample type.
        sample_location: CGM sample location.
        e2e_crc: E2E-CRC value.

    """

    features: CGMFeatureFlags
    cgm_type: CGMType
    sample_location: CGMSampleLocation
    e2e_crc: int


class CGMFeatureCharacteristic(BaseCharacteristic[CGMFeatureData]):
    """CGM Feature characteristic (0x2AA8).

    Reports the supported features, sample type, sample location, and
    E2E-CRC for a CGM sensor.  Fixed 6-byte structure.
    """

    expected_type = CGMFeatureData
    expected_length: int = 6

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> CGMFeatureData:
        """Parse CGM Feature from raw BLE bytes.

        Args:
            data: Raw bytearray from BLE characteristic (6 bytes).
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            CGMFeatureData with parsed feature flags, type, and location.

        """
        # 24-bit feature flags (little-endian, 3 bytes)
        features_raw = data[0] | (data[1] << 8) | (data[2] << 16)
        features = CGMFeatureFlags(features_raw)

        # Type-Sample Location: lower nibble = type, upper nibble = location
        type_location_byte = data[3]
        cgm_type = CGMType(type_location_byte & _NIBBLE_MASK)
        sample_location = CGMSampleLocation((type_location_byte >> _NIBBLE_SHIFT) & _NIBBLE_MASK)

        e2e_crc = DataParser.parse_int16(data, 4, signed=False)

        return CGMFeatureData(
            features=features,
            cgm_type=cgm_type,
            sample_location=sample_location,
            e2e_crc=e2e_crc,
        )

    def _encode_value(self, data: CGMFeatureData) -> bytearray:
        """Encode CGMFeatureData back to BLE bytes.

        Args:
            data: CGMFeatureData instance.

        Returns:
            Encoded bytearray (6 bytes).

        """
        features_int = int(data.features)
        result = bytearray(
            [
                features_int & 0xFF,
                (features_int >> 8) & 0xFF,
                (features_int >> 16) & 0xFF,
            ]
        )

        type_location = (data.cgm_type & _NIBBLE_MASK) | ((data.sample_location & _NIBBLE_MASK) << _NIBBLE_SHIFT)
        result.append(type_location)

        result.extend(DataParser.encode_int16(data.e2e_crc, signed=False))
        return result
