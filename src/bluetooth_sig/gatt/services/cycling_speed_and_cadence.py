"""Cycling Speed and Cadence Service implementation."""

from dataclasses import dataclass

from ..characteristics.csc_measurement import CSCMeasurementCharacteristic
from .base import BaseGattService


@dataclass
class CyclingSpeedAndCadenceService(BaseGattService):
    """Cycling Speed and Cadence Service implementation (0x1816).

    Used for cycling sensors that measure wheel and crank revolutions.
    Contains the CSC Measurement characteristic for cycling metrics.
    """

    @classmethod
    def get_expected_characteristics(cls) -> dict[str, type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "CSC Measurement": CSCMeasurementCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> dict[str, type]:
        """Get the required characteristics for this service by name and class."""
        return {
            "CSC Measurement": CSCMeasurementCharacteristic,
        }
