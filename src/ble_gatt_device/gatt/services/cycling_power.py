"""Cycling Power Service implementation."""

from dataclasses import dataclass
from typing import Dict, Type

from ..characteristics.cycling_power_control_point import (
    CyclingPowerControlPointCharacteristic,
)
from ..characteristics.cycling_power_feature import CyclingPowerFeatureCharacteristic
from ..characteristics.cycling_power_measurement import (
    CyclingPowerMeasurementCharacteristic,
)
from ..characteristics.cycling_power_vector import CyclingPowerVectorCharacteristic
from .base import BaseGattService


@dataclass
class CyclingPowerService(BaseGattService):
    """Cycling Power Service implementation (0x1818).

    Used for cycling power meters that measure power output in watts.
    Supports instantaneous power, force/torque vectors, and control functions.
    """

    @classmethod
    def get_expected_characteristics(cls) -> Dict[str, Type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "Cycling Power Measurement": CyclingPowerMeasurementCharacteristic,
            "Cycling Power Feature": CyclingPowerFeatureCharacteristic,
            "Cycling Power Vector": CyclingPowerVectorCharacteristic,
            "Cycling Power Control Point": CyclingPowerControlPointCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> Dict[str, Type]:
        """Get the required characteristics for this service by name and class."""
        return {
            "Cycling Power Measurement": CyclingPowerMeasurementCharacteristic,
            "Cycling Power Feature": CyclingPowerFeatureCharacteristic,
        }
