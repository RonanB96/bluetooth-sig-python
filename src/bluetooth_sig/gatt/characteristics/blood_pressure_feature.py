"""Blood Pressure Feature characteristic implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ...types.gatt_enums import ValueType
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class BloodPressureFeatures(IntFlag):
    """Blood Pressure Feature flags as per Bluetooth SIG specification."""

    BODY_MOVEMENT_DETECTION = 0x01
    CUFF_FIT_DETECTION = 0x02
    IRREGULAR_PULSE_DETECTION = 0x04
    PULSE_RATE_RANGE_DETECTION = 0x08
    MEASUREMENT_POSITION_DETECTION = 0x10
    MULTIPLE_BOND_SUPPORT = 0x20


class BloodPressureFeatureData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Blood Pressure Feature characteristic."""

    features_bitmap: int
    body_movement_detection_support: bool
    cuff_fit_detection_support: bool
    irregular_pulse_detection_support: bool
    pulse_rate_range_detection_support: bool
    measurement_position_detection_support: bool
    multiple_bond_support: bool


class BloodPressureFeatureCharacteristic(BaseCharacteristic):
    """Blood Pressure Feature characteristic (0x2A49).

    Used to expose the supported features of a blood pressure monitoring
    device. Indicates which optional measurements and capabilities are
    available.
    """

    _manual_value_type: ValueType | str | None = ValueType.DICT  # Override since decode_value returns dataclass

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> BloodPressureFeatureData:
        """Parse blood pressure feature data according to Bluetooth specification.

        Format: Features(2) - 16-bit bitmap indicating supported features.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext providing surrounding context (may be None).

        Returns:
            BloodPressureFeatureData containing parsed feature bitmap and capabilities.

        """
        if len(data) < 2:
            raise ValueError("Blood Pressure Feature data must be at least 2 bytes")

        features_bitmap = DataParser.parse_int16(data, 0, signed=False)

        body_movement_detection = bool(features_bitmap & BloodPressureFeatures.BODY_MOVEMENT_DETECTION)
        cuff_fit_detection = bool(features_bitmap & BloodPressureFeatures.CUFF_FIT_DETECTION)
        irregular_pulse_detection = bool(features_bitmap & BloodPressureFeatures.IRREGULAR_PULSE_DETECTION)
        pulse_rate_range_detection = bool(features_bitmap & BloodPressureFeatures.PULSE_RATE_RANGE_DETECTION)
        measurement_position_detection = bool(features_bitmap & BloodPressureFeatures.MEASUREMENT_POSITION_DETECTION)
        multiple_bond_support = bool(features_bitmap & BloodPressureFeatures.MULTIPLE_BOND_SUPPORT)

        return BloodPressureFeatureData(
            features_bitmap=features_bitmap,
            body_movement_detection_support=body_movement_detection,
            cuff_fit_detection_support=cuff_fit_detection,
            irregular_pulse_detection_support=irregular_pulse_detection,
            pulse_rate_range_detection_support=pulse_rate_range_detection,
            measurement_position_detection_support=measurement_position_detection,
            multiple_bond_support=multiple_bond_support,
        )

    def encode_value(self, data: BloodPressureFeatureData) -> bytearray:
        """Encode BloodPressureFeatureData back to bytes.

        Args:
            data: BloodPressureFeatureData instance to encode

        Returns:
            Encoded bytes representing the blood pressure features

        """
        return DataParser.encode_int16(data.features_bitmap, signed=False)
