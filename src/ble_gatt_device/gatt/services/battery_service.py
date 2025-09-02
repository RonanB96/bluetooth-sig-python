"""Battery Service implementation."""

from dataclasses import dataclass

from ..characteristics.battery_level import BatteryLevelCharacteristic
from ..characteristics.battery_power_state import BatteryPowerStateCharacteristic
from .base import BaseGattService


@dataclass
class BatteryService(BaseGattService):
    """Battery Service implementation.

    Contains characteristics related to battery information:
    - Battery Level - Required
    - Battery Level Status - Optional
    """

    @classmethod
    def get_expected_characteristics(cls) -> dict[str, type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "Battery Level": BatteryLevelCharacteristic,
            "Battery Level Status": BatteryPowerStateCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> dict[str, type]:
        """Get the required characteristics for this service by name and class."""
        return {
            "Battery Level": BatteryLevelCharacteristic,
        }
