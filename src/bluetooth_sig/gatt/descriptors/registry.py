"""Descriptor registry and resolution."""

from __future__ import annotations

from ...types.uuid import BluetoothUUID
from .base import BaseDescriptor


class DescriptorRegistry:
    """Registry for descriptor classes."""

    _registry: dict[str, type[BaseDescriptor]] = {}

    @classmethod
    def register(cls, descriptor_class: type[BaseDescriptor]) -> None:
        """Register a descriptor class."""
        # Create an instance to resolve the UUID
        try:
            instance = descriptor_class()
            uuid_str = str(instance.uuid)
            cls._registry[uuid_str] = descriptor_class
        except (ValueError, TypeError, AttributeError):
            # If we can't create an instance or resolve UUID, skip registration
            pass

    @classmethod
    def get_descriptor_class(cls, uuid: str) -> type[BaseDescriptor] | None:
        """Get descriptor class for UUID."""
        # Convert to BluetoothUUID and use full form for lookup
        try:
            uuid_obj = BluetoothUUID(uuid)
            full_uuid_str = uuid_obj.dashed_form
            return cls._registry.get(full_uuid_str)
        except ValueError:
            return None

    @classmethod
    def create_descriptor(cls, uuid: str) -> BaseDescriptor | None:
        """Create descriptor instance for UUID."""
        descriptor_class = cls.get_descriptor_class(uuid)
        if descriptor_class:
            try:
                return descriptor_class()
            except (ValueError, TypeError, AttributeError):
                return None
        return None

    @classmethod
    def list_registered_descriptors(cls) -> list[str]:
        """List all registered descriptor UUIDs."""
        return list(cls._registry.keys())
