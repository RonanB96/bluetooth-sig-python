"""Descriptor registry and resolution."""

from __future__ import annotations

import inspect
import logging
import threading
from importlib import import_module
from typing import ClassVar

from ...types.uuid import BluetoothUUID
from ..registry_utils import ModuleDiscovery
from .base import BaseDescriptor

logger = logging.getLogger(__name__)


class DescriptorRegistry:
    """Registry for descriptor classes."""

    _registry: ClassVar[dict[str, type[BaseDescriptor]]] = {}
    _loaded: ClassVar[bool] = False
    _lock: ClassVar[threading.RLock] = threading.RLock()
    _MODULE_EXCLUSIONS: ClassVar[set[str]] = {"__init__", "__main__", "_export_map", "base", "registry"}

    @classmethod
    def _ensure_loaded(cls) -> None:
        with cls._lock:
            if cls._loaded:
                return
            cls._register_builtins()
            cls._loaded = True

    @classmethod
    def _register_builtins(cls) -> None:
        package_name = __package__ or "bluetooth_sig.gatt.descriptors"
        module_names = ModuleDiscovery.iter_module_names(package_name, cls._MODULE_EXCLUSIONS)
        for module_name in module_names:
            module = import_module(module_name)
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if not isinstance(obj, type) or not issubclass(obj, BaseDescriptor):
                    continue
                if obj is BaseDescriptor or getattr(obj, "_is_template", False):
                    continue
                if obj.__module__ != module.__name__:
                    continue
                cls.register(obj)

    @classmethod
    def register(cls, descriptor_class: type[BaseDescriptor]) -> None:
        """Register a descriptor class."""
        try:
            instance = descriptor_class()
            uuid_str = str(instance.uuid)
            cls._registry[uuid_str] = descriptor_class
        except (ValueError, TypeError, AttributeError):
            logger.warning("Failed to register descriptor class %s", descriptor_class.__name__)

    @classmethod
    def get_descriptor_class(cls, uuid: str | BluetoothUUID | int) -> type[BaseDescriptor] | None:
        """Get descriptor class for UUID.

        Args:
            uuid: The descriptor UUID

        Returns:
            Descriptor class if found, None otherwise

        Raises:
            ValueError: If uuid format is invalid
        """
        cls._ensure_loaded()
        uuid_obj = BluetoothUUID(uuid)
        full_uuid_str = uuid_obj.dashed_form
        return cls._registry.get(full_uuid_str)

    @classmethod
    def create_descriptor(cls, uuid: str | BluetoothUUID | int) -> BaseDescriptor | None:
        """Create descriptor instance for UUID.

        Args:
            uuid: The descriptor UUID

        Returns:
            Descriptor instance if found, None otherwise

        Raises:
            ValueError: If uuid format is invalid
        """
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
        cls._ensure_loaded()
        return list(cls._registry.keys())
