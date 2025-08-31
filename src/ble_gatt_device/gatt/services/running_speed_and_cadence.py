"""Running Speed and Cadence Service implementation."""

from dataclasses import dataclass
from typing import Dict, Type

from .base import BaseGattService
from ..characteristics.rsc_measurement import RSCMeasurementCharacteristic


@dataclass
class RunningSpeedAndCadenceService(BaseGattService):
    """Running Speed and Cadence Service implementation (0x1814).

    Used for running sensors that measure speed, cadence, stride length, and distance.
    Contains the RSC Measurement characteristic for running metrics.
    """

    @classmethod
    def get_expected_characteristics(cls) -> Dict[str, Type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "RSC Measurement": RSCMeasurementCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> Dict[str, Type]:
        """Get the required characteristics for this service by name and class."""
        return {
            "RSC Measurement": RSCMeasurementCharacteristic,
        }