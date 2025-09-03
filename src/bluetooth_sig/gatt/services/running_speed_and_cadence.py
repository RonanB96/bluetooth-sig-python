"""Running Speed and Cadence Service implementation."""

from dataclasses import dataclass

from ..characteristics.rsc_measurement import RSCMeasurementCharacteristic
from .base import BaseGattService


@dataclass
class RunningSpeedAndCadenceService(BaseGattService):
    """Running Speed and Cadence Service implementation (0x1814).

    Used for running sensors that measure speed, cadence, stride length, and distance.
    Contains the RSC Measurement characteristic for running metrics.
    """

    @classmethod
    def get_expected_characteristics(cls) -> dict[str, type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "RSC Measurement": RSCMeasurementCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> dict[str, type]:
        """Get the required characteristics for this service by name and class."""
        return {
            "RSC Measurement": RSCMeasurementCharacteristic,
        }
