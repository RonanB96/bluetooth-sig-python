"""Weight Scale Service implementation."""

from dataclasses import dataclass
from typing import Dict, Type

from ..characteristics.weight_measurement import WeightMeasurementCharacteristic
from ..characteristics.weight_scale_feature import WeightScaleFeatureCharacteristic
from .base import BaseGattService


@dataclass
class WeightScaleService(BaseGattService):
    """Weight Scale Service implementation (0x181D).

    Used for smart scale devices that measure weight and related body metrics.
    Contains Weight Measurement and Weight Scale Feature characteristics.
    """

    @classmethod
    def get_expected_characteristics(cls) -> Dict[str, Type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "Weight Measurement": WeightMeasurementCharacteristic,
            "Weight Scale Feature": WeightScaleFeatureCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> Dict[str, Type]:
        """Get the required characteristics for this service by name and class."""
        return {
            "Weight Measurement": WeightMeasurementCharacteristic,
        }
