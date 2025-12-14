"""Format Types registry for Bluetooth SIG characteristic format type definitions."""

from __future__ import annotations

import logging

import msgspec

from bluetooth_sig.registry.base import BaseGenericRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path
from bluetooth_sig.types.registry.formattypes import FormatTypeInfo

logger = logging.getLogger(__name__)


class FormatTypesRegistry(BaseGenericRegistry[FormatTypeInfo]):
    """Registry for Bluetooth characteristic format types with lazy loading.

    This registry loads format type definitions from the official Bluetooth SIG
    assigned_numbers YAML file, providing authoritative format type information
    from the specification.
    """

    def __init__(self) -> None:
        """Initialize the format types registry."""
        super().__init__()
        self._format_types: dict[int, FormatTypeInfo] = {}
        self._format_types_by_name: dict[str, FormatTypeInfo] = {}

    def _load(self) -> None:
        """Perform the actual loading of format types data."""
        base_path = find_bluetooth_sig_path()
        if not base_path:
            logger.warning("Bluetooth SIG path not found. Format types registry will be empty.")
            self._loaded = True
            return

        yaml_path = base_path.parent / "core" / "formattypes.yaml"
        if not yaml_path.exists():
            logger.warning(
                "Format types YAML file not found at %s. Registry will be empty.",
                yaml_path,
            )
            self._loaded = True
            return

        try:
            with yaml_path.open("r", encoding="utf-8") as f:
                data = msgspec.yaml.decode(f.read())

            if not data or "formattypes" not in data:
                logger.warning("Invalid format types YAML format. Registry will be empty.")
                self._loaded = True
                return

            for item in data["formattypes"]:
                value = item.get("value")
                short_name = item.get("short_name")
                description = item.get("description")
                exponent = item.get("exponent")
                size = item.get("size")

                if value is None or not short_name:
                    continue

                # Handle hex values in YAML (e.g., 0x01)
                if isinstance(value, str):
                    value = int(value, 16)

                format_type_info = FormatTypeInfo(
                    value=value,
                    short_name=short_name,
                    description=description,
                    exponent=exponent,
                    size=size,
                )

                self._format_types[value] = format_type_info
                self._format_types_by_name[short_name.lower()] = format_type_info

            logger.info("Loaded %d format types from specification", len(self._format_types))
        except (FileNotFoundError, OSError, msgspec.DecodeError, KeyError) as e:
            logger.warning(
                "Failed to load format types from YAML: %s. Registry will be empty.",
                e,
            )

        self._loaded = True

    def get_format_type_info(self, value: int) -> FormatTypeInfo | None:
        """Get format type info by value (lazy loads on first call).

        Args:
            value: The format type value (e.g., 0x01 for boolean)

        Returns:
            FormatTypeInfo object, or None if not found
        """
        self._ensure_loaded()
        with self._lock:
            return self._format_types.get(value)

    def get_format_type_by_name(self, name: str) -> FormatTypeInfo | None:
        """Get format type info by short name (lazy loads on first call).

        Args:
            name: Format type short name (case-insensitive, e.g., "boolean", "utf8s")

        Returns:
            FormatTypeInfo object, or None if not found
        """
        self._ensure_loaded()
        with self._lock:
            return self._format_types_by_name.get(name.lower())

    def is_known_format_type(self, value: int) -> bool:
        """Check if format type is known (lazy loads on first call).

        Args:
            value: The format type value to check

        Returns:
            True if the format type is registered, False otherwise
        """
        self._ensure_loaded()
        with self._lock:
            return value in self._format_types

    def get_all_format_types(self) -> dict[int, FormatTypeInfo]:
        """Get all registered format types (lazy loads on first call).

        Returns:
            Dictionary mapping format type values to FormatTypeInfo objects
        """
        self._ensure_loaded()
        with self._lock:
            return self._format_types.copy()


# Global singleton instance
format_types_registry = FormatTypesRegistry()
