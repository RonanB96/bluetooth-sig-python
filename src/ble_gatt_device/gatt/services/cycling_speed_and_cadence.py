"""Cycling Speed and Cadence Service implementation."""

from dataclasses import dataclass
from typing import Dict, Type

from .base import BaseGattService
from ..characteristics.csc_measurement import CSCMeasurementCharacteristic


@dataclass
class CyclingSpeedAndCadenceService(BaseGattService):
    """Cycling Speed and Cadence Service implementation (0x1816).

    Used for cycling sensors that measure wheel and crank revolutions.
    Contains the CSC Measurement characteristic for cycling metrics.
    """

    @classmethod
    def get_expected_characteristics(cls) -> Dict[str, Type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "CSC Measurement": CSCMeasurementCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> Dict[str, Type]:
        """Get the required characteristics for this service by name and class."""
        return {
            "CSC Measurement": CSCMeasurementCharacteristic,
        }