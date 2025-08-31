"""Battery Service implementation."""

from dataclasses import dataclass
from typing import Dict, Type

from ..characteristics.battery_level import BatteryLevelCharacteristic
from .base import BaseGattService


@dataclass
class BatteryService(BaseGattService):
    """Battery Service implementation.

    Contains characteristics related to battery information:
    - Battery Level - Required
    """

    @classmethod
    def get_expected_characteristics(cls) -> Dict[str, Type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "Battery Level": BatteryLevelCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> Dict[str, Type]:
        """Get the required characteristics for this service by name and class."""
        return {
            "Battery Level": BatteryLevelCharacteristic,
        }
