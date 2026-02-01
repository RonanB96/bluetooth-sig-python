"""High Intensity Exercise Threshold characteristic (0x2B4D)."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

# Field selector values
_FIELD_SELECTOR_ENERGY = 1
_FIELD_SELECTOR_MET = 2
_FIELD_SELECTOR_HR_PERCENTAGE = 3

# Minimum data lengths for each field selector
_MIN_LENGTH_ENERGY = 3  # 1 byte selector + 2 bytes uint16
_MIN_LENGTH_MET = 2  # 1 byte selector + 1 byte uint8
_MIN_LENGTH_HR = 2  # 1 byte selector + 1 byte uint8


class HighIntensityExerciseThresholdData(msgspec.Struct):
    """High Intensity Exercise Threshold parsed data.

    Attributes:
        field_selector: Field selector indicating which threshold is present (1, 2, or 3)
        threshold_energy_expenditure: Energy expenditure in joules (field_selector=1)
        threshold_metabolic_equivalent: Metabolic equivalent in MET (field_selector=2)
        threshold_percentage_max_heart_rate: Heart rate percentage (field_selector=3)
    """

    field_selector: int
    threshold_energy_expenditure: int | None = None
    threshold_metabolic_equivalent: float | None = None
    threshold_percentage_max_heart_rate: int | None = None


class HighIntensityExerciseThresholdCharacteristic(BaseCharacteristic[HighIntensityExerciseThresholdData]):
    """High Intensity Exercise Threshold characteristic (0x2B4D).

    org.bluetooth.characteristic.high_intensity_exercise_threshold

    High Intensity Exercise Threshold characteristic with conditional fields.

    Structure (variable length):
    - Field Selector (uint8): 1 byte - determines which threshold field follows
      - 1 = Threshold as Energy Expenditure per Hour (uint16, 0 or 2 bytes)
      - 2 = Threshold as Metabolic Equivalent (uint8, 0 or 1 byte)
      - 3 = Threshold as Percentage of Maximum Heart Rate (uint8, 0 or 1 byte)

    Total payload: 1-3 bytes
    """

    # YAML specifies variable fields based on Field Selector value
    min_length: int | None = 1
    max_length: int | None = 3

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> HighIntensityExerciseThresholdData:
        """Parse High Intensity Exercise Threshold with conditional fields.

        Args:
            data: Raw bytes (1-3 bytes)
            ctx: Optional context
            validate: Whether to validate ranges (default True)

        Returns:
            HighIntensityExerciseThresholdData with field_selector and optional threshold
        """
        field_selector = int(data[0])
        threshold_energy = None
        threshold_met = None
        threshold_hr = None

        # Parse optional threshold field based on selector
        if field_selector == _FIELD_SELECTOR_ENERGY and len(data) >= _MIN_LENGTH_ENERGY:
            # Energy Expenditure per Hour (uint16, resolution 1000 J)
            threshold = DataParser.parse_int16(data, 1, signed=False)
            threshold_energy = threshold * 1000  # Convert to joules
        elif field_selector == _FIELD_SELECTOR_MET and len(data) >= _MIN_LENGTH_MET:
            # Metabolic Equivalent (uint8, resolution 0.1 MET)
            threshold = int(data[1])
            threshold_met = threshold * 0.1
        elif field_selector == _FIELD_SELECTOR_HR_PERCENTAGE and len(data) >= _MIN_LENGTH_HR:
            # Percentage of Maximum Heart Rate (uint8)
            threshold = int(data[1])
            threshold_hr = threshold

        return HighIntensityExerciseThresholdData(
            field_selector=field_selector,
            threshold_energy_expenditure=threshold_energy,
            threshold_metabolic_equivalent=threshold_met,
            threshold_percentage_max_heart_rate=threshold_hr,
        )

    def _encode_value(self, data: HighIntensityExerciseThresholdData) -> bytearray:
        """Encode High Intensity Exercise Threshold.

        Args:
            data: HighIntensityExerciseThresholdData instance

        Returns:
            Encoded bytes (1-3 bytes)
        """
        result = bytearray([data.field_selector])

        if data.field_selector == _FIELD_SELECTOR_ENERGY and data.threshold_energy_expenditure is not None:
            # Convert joules back to 1000 J units
            energy_value = int(data.threshold_energy_expenditure / 1000)
            result.extend(DataParser.encode_int16(energy_value, signed=False))
        elif data.field_selector == _FIELD_SELECTOR_MET and data.threshold_metabolic_equivalent is not None:
            # Convert 0.1 MET units back to uint8
            met_value = int(data.threshold_metabolic_equivalent / 0.1)
            result.append(met_value)
        elif (
            data.field_selector == _FIELD_SELECTOR_HR_PERCENTAGE
            and data.threshold_percentage_max_heart_rate is not None
        ):
            hr_value = int(data.threshold_percentage_max_heart_rate)
            result.append(hr_value)

        return result
