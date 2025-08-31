"""Body Composition Service implementation."""

from dataclasses import dataclass
from typing import Dict, Type

from ..characteristics.body_composition_measurement import (
    BodyCompositionMeasurementCharacteristic,
)
from ..characteristics.body_composition_feature import (
    BodyCompositionFeatureCharacteristic,
)
from .base import BaseGattService


@dataclass
class BodyCompositionService(BaseGattService):
    """Body Composition Service implementation (0x181B).

    Used for smart scale devices that measure body composition metrics including
    body fat percentage, muscle mass, bone mass, and water percentage.
    Contains Body Composition Measurement and Body Composition Feature characteristics.
    """

    @classmethod
    def get_expected_characteristics(cls) -> Dict[str, Type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "Body Composition Measurement": BodyCompositionMeasurementCharacteristic,
            "Body Composition Feature": BodyCompositionFeatureCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> Dict[str, Type]:
        """Get the required characteristics for this service by name and class."""
        return {
            "Body Composition Measurement": BodyCompositionMeasurementCharacteristic,
        }