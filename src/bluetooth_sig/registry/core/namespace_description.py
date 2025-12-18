"""Namespace Description registry for CPF descriptor description field resolution.

The CPF (Characteristic Presentation Format) descriptor has a description field
that, when namespace=0x01 (Bluetooth SIG), can be resolved to human-readable
names like "first", "left", "front", etc.

Used during CPF descriptor parsing to provide description_name resolution.
"""

from __future__ import annotations

import logging

import msgspec

from bluetooth_sig.registry.base import BaseGenericRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path
from bluetooth_sig.types.registry.namespace import NamespaceDescriptionInfo

logger = logging.getLogger(__name__)


class NamespaceDescriptionRegistry(BaseGenericRegistry[NamespaceDescriptionInfo]):
    """Registry for Bluetooth SIG namespace description values with lazy loading.

    This registry loads namespace description definitions from the official
    Bluetooth SIG assigned_numbers YAML file (namespace.yaml), enabling
    resolution of CPF description field values to human-readable names.

    The description field in CPF is a 16-bit value that, when namespace=0x01
    (Bluetooth SIG Assigned Numbers), can be resolved to names like:
    - 0x0001 → "first"
    - 0x010D → "left"
    - 0x010E → "right"
    - 0x0102 → "top"

    Examples:
        >>> from bluetooth_sig.registry.core.namespace_description import namespace_description_registry
        >>> info = namespace_description_registry.get_description_info(0x010D)
        >>> info.name
        'left'
    """

    def __init__(self) -> None:
        """Initialize the namespace description registry."""
        super().__init__()
        self._descriptions: dict[int, NamespaceDescriptionInfo] = {}
        self._descriptions_by_name: dict[str, NamespaceDescriptionInfo] = {}

    def _load(self) -> None:
        """Perform the actual loading of namespace description data."""
        base_path = find_bluetooth_sig_path()
        if not base_path:
            logger.warning("Bluetooth SIG path not found. Namespace description registry will be empty.")
            self._loaded = True
            return

        yaml_path = base_path.parent / "core" / "namespace.yaml"
        if not yaml_path.exists():
            logger.warning(
                "Namespace YAML file not found at %s. Registry will be empty.",
                yaml_path,
            )
            self._loaded = True
            return

        try:
            with yaml_path.open("r", encoding="utf-8") as f:
                data = msgspec.yaml.decode(f.read())

            if not data or "namespace" not in data:
                logger.warning("Invalid namespace YAML format. Registry will be empty.")
                self._loaded = True
                return

            for item in data["namespace"]:
                value = item.get("value")
                name = item.get("name")

                if value is None or not name:
                    continue

                # Handle hex values in YAML (e.g., 0x010D)
                if isinstance(value, str):
                    value = int(value, 16)

                description_info = NamespaceDescriptionInfo(
                    value=value,
                    name=name,
                )

                self._descriptions[value] = description_info
                self._descriptions_by_name[name.lower()] = description_info

            logger.info("Loaded %d namespace descriptions from specification", len(self._descriptions))
        except (FileNotFoundError, OSError, msgspec.DecodeError, KeyError) as e:
            logger.warning(
                "Failed to load namespace descriptions from YAML: %s. Registry will be empty.",
                e,
            )

        self._loaded = True

    def get_description_info(self, value: int) -> NamespaceDescriptionInfo | None:
        """Get description info by value (lazy loads on first call).

        Args:
            value: The description value (e.g., 0x010D for "left")

        Returns:
            NamespaceDescriptionInfo object, or None if not found
        """
        self._ensure_loaded()
        with self._lock:
            return self._descriptions.get(value)

    def get_description_by_name(self, name: str) -> NamespaceDescriptionInfo | None:
        """Get description info by name (lazy loads on first call).

        Args:
            name: Description name (case-insensitive, e.g., "left", "first")

        Returns:
            NamespaceDescriptionInfo object, or None if not found
        """
        self._ensure_loaded()
        with self._lock:
            return self._descriptions_by_name.get(name.lower())

    def is_known_description(self, value: int) -> bool:
        """Check if description value is known (lazy loads on first call).

        Args:
            value: The description value to check

        Returns:
            True if the description is registered, False otherwise
        """
        self._ensure_loaded()
        with self._lock:
            return value in self._descriptions

    def get_all_descriptions(self) -> dict[int, NamespaceDescriptionInfo]:
        """Get all registered namespace descriptions (lazy loads on first call).

        Returns:
            Dictionary mapping description values to NamespaceDescriptionInfo objects
        """
        self._ensure_loaded()
        with self._lock:
            return self._descriptions.copy()

    def resolve_description_name(self, value: int) -> str | None:
        """Resolve a description value to its string name.

        Convenience method for CPF parsing that returns the description
        name directly, or None if unknown.

        Args:
            value: The description value to resolve

        Returns:
            Description name string (e.g., "left", "first"), or None if unknown
        """
        info = self.get_description_info(value)
        return info.name if info else None


# Global singleton instance
namespace_description_registry = NamespaceDescriptionRegistry()
