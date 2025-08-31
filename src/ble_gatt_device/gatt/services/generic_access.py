"""Generic Access Service implementation."""

from dataclasses import dataclass
from typing import Dict, Type

from .base import BaseGattService
from ..characteristics.generic_access import (
    AppearanceCharacteristic,
    DeviceNameCharacteristic,
)


@dataclass
class GenericAccessService(BaseGattService):
    """Generic Access Service implementation.

    Contains characteristics that expose basic device access information:
    - Device Name - Required
    - Appearance - Optional
    """

    _service_name: str = "GAP"

    @classmethod
    def get_expected_characteristics(cls) -> Dict[str, Type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "Device Name": DeviceNameCharacteristic,
            "Appearance": AppearanceCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> Dict[str, Type]:
        """Get the required characteristics for this service by name and class."""
        return {
            "Device Name": DeviceNameCharacteristic,
        }
