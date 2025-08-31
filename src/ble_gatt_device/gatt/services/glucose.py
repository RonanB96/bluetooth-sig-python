"""Glucose Service implementation."""

from dataclasses import dataclass
from typing import Dict, Type

from ..characteristics.glucose_feature import GlucoseFeatureCharacteristic
from ..characteristics.glucose_measurement import GlucoseMeasurementCharacteristic
from ..characteristics.glucose_measurement_context import (
    GlucoseMeasurementContextCharacteristic,
)
from .base import BaseGattService


@dataclass
class GlucoseService(BaseGattService):
    """Glucose Service implementation (0x1808).

    Used for glucose monitoring devices including continuous glucose monitors (CGMs)
    and traditional glucose meters. Provides comprehensive glucose measurement data
    with context and device capabilities.
    """

    @classmethod
    def get_expected_characteristics(cls) -> Dict[str, Type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "Glucose Measurement": GlucoseMeasurementCharacteristic,
            "Glucose Measurement Context": GlucoseMeasurementContextCharacteristic,
            "Glucose Feature": GlucoseFeatureCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> Dict[str, Type]:
        """Get the required characteristics for this service by name and class."""
        return {
            "Glucose Measurement": GlucoseMeasurementCharacteristic,
            "Glucose Feature": GlucoseFeatureCharacteristic,
        }