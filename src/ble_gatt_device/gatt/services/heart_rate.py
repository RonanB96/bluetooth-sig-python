"""Heart Rate Service implementation."""

from dataclasses import dataclass
from typing import Dict, Type

from ..characteristics.heart_rate_measurement import HeartRateMeasurementCharacteristic
from .base import BaseGattService


@dataclass
class HeartRateService(BaseGattService):
    """Heart Rate Service implementation (0x180D).

    Used for heart rate monitoring devices.
    Contains the Heart Rate Measurement characteristic for heart rate data with optional
    RR-intervals and energy expenditure.
    """

    @classmethod
    def get_expected_characteristics(cls) -> Dict[str, Type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "Heart Rate Measurement": HeartRateMeasurementCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> Dict[str, Type]:
        """Get the required characteristics for this service by name and class."""
        return {
            "Heart Rate Measurement": HeartRateMeasurementCharacteristic,
        }
