"""Generic Attribute Service implementation."""

from dataclasses import dataclass

from .base import BaseGattService


@dataclass
class GenericAttributeService(BaseGattService):
    """Generic Attribute Service implementation.

    The GATT Service contains information about the GATT database and is
    primarily used for service discovery and attribute access.

    This service typically contains:
    - Service Changed characteristic (optional)
    """

    _service_name: str = "GATT"

    @classmethod
    def get_expected_characteristics(cls) -> dict[str, type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            # Service Changed characteristic is optional
        }

    @classmethod
    def get_required_characteristics(cls) -> dict[str, type]:
        """Get the required characteristics for this service by name and class."""
        return {}
