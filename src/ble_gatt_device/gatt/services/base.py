"""Base class for GATT services."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional, Set, Type

from ..characteristics import BaseCharacteristic
from ..uuid_registry import uuid_registry

# Type aliases
GattCharacteristic = BaseCharacteristic


@dataclass
class BaseGattService(ABC):
    """Base class for all GATT services."""

    # Instance variables
    characteristics: Dict[str, BaseCharacteristic] = field(default_factory=dict)

    @property
    def SERVICE_UUID(self) -> str:
        """Get the service UUID from registry based on class name."""
        # First try explicit service name if set
        if hasattr(self, "_service_name") and self._service_name:
            info = uuid_registry.get_service_info(self._service_name)
            if info:
                return info.uuid

        # Convert class name to standard format and try all possibilities
        name = self.__class__.__name__

        # Try different name formats:
        # 1. Full class name (e.g., BatteryService)
        # 2. Without 'Service' suffix (e.g., Battery)
        # 3. As standard service ID
        # (e.g., org.bluetooth.service.battery_service)
        # Format name for lookup
        service_name = name
        if name.endswith("Service"):
            service_name = name[:-7]  # Remove 'Service' suffix

        # Split on camelCase and convert to space-separated
        words = re.findall("[A-Z][^A-Z]*", service_name)
        display_name = " ".join(words)

        # Try different name formats
        names_to_try = [
            name,  # Full class name (e.g. BatteryService)
            service_name,  # Without 'Service' suffix
            display_name,  # Space-separated (e.g. Environmental Sensing)
            display_name + " Service",  # With Service suffix
            # Service-specific format
            "org.bluetooth.service." + "_".join(words).lower(),
        ]

        # Try each name format
        for try_name in names_to_try:
            info = uuid_registry.get_service_info(try_name)
            if info:
                return info.uuid

        raise ValueError(f"No UUID found for service: {name}")

    @property
    def name(self) -> str:
        """Get the service name from UUID registry."""
        info = uuid_registry.get_service_info(self.SERVICE_UUID)
        return info.name if info else f"Unknown Service ({self.SERVICE_UUID})"

    @property
    def summary(self) -> str:
        """Get the service summary."""
        info = uuid_registry.get_service_info(self.SERVICE_UUID)
        return info.summary if info else ""

    @classmethod
    def matches_uuid(cls, uuid: str) -> bool:
        """Check if this service matches the given UUID."""
        try:
            return cls().SERVICE_UUID.lower() == uuid.lower()
        except ValueError:
            return False

    @classmethod
    @abstractmethod
    def get_expected_characteristics(cls) -> Dict[str, Type]:
        """Get the expected characteristics for this service by name and class.

        Returns:
            Dict mapping characteristic name to characteristic class
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_required_characteristics(cls) -> Dict[str, Type]:
        """Get the required characteristics for this service by name and class.

        Returns:
            Dict mapping characteristic name to characteristic class
        """
        raise NotImplementedError

    def get_expected_characteristic_uuids(self) -> Set[str]:
        """Get the set of expected characteristic UUIDs for this service."""
        expected_uuids = set()
        for char_name, _ in self.get_expected_characteristics().items():
            char_info = uuid_registry.get_characteristic_info(char_name)
            if char_info:
                expected_uuids.add(char_info.uuid)
        return expected_uuids

    def get_required_characteristic_uuids(self) -> Set[str]:
        """Get the set of required characteristic UUIDs for this service."""
        required_uuids = set()
        for char_name, _ in self.get_required_characteristics().items():
            char_info = uuid_registry.get_characteristic_info(char_name)
            if char_info:
                required_uuids.add(char_info.uuid)
        return required_uuids

    @abstractmethod
    def process_characteristics(self, characteristics: Dict[str, Dict]) -> None:
        """Process the characteristics for this service.

        Args:
            characteristics: Dict mapping UUID to characteristic properties
        """
        # Abstract method, to be implemented by subclasses
        raise NotImplementedError

    def get_characteristic(self, uuid: str) -> Optional[GattCharacteristic]:
        """Get a characteristic by UUID."""
        return self.characteristics.get(uuid.lower())

    @property
    def supported_characteristics(self) -> Set[str]:
        """Get the set of characteristic UUIDs supported by this service."""
        return set(self.characteristics.keys())
