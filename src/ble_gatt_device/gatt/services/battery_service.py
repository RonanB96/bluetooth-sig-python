"""Battery Service implementation."""

from dataclasses import dataclass
from typing import Dict, Type

from .base import BaseGattService
from ..characteristics import CharacteristicRegistry
from ..characteristics.battery_level import BatteryLevelCharacteristic


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

    def process_characteristics(self, characteristics: Dict[str, Dict]) -> None:
        """Process battery service characteristics."""
        for uuid, props in characteristics.items():
            uuid = uuid.replace("-", "").upper()
            char = CharacteristicRegistry.create_characteristic(
                uuid=uuid, properties=set(props.get("properties", []))
            )
            if char:
                self.characteristics[uuid] = char
