"""AD Types registry for Bluetooth SIG advertising data type definitions."""

from __future__ import annotations

import logging

import msgspec

from bluetooth_sig.registry.base import BaseRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_core_path
from bluetooth_sig.types.advertising import ADTypeInfo

logger = logging.getLogger(__name__)


class ADTypesRegistry(BaseRegistry[ADTypeInfo]):
    """Registry for Bluetooth advertising data types.

    This registry loads AD type definitions from the official Bluetooth SIG
    assigned_numbers YAML file, providing authoritative AD type information
    from the specification.
    """

    def __init__(self) -> None:
        """Initialize the AD types registry."""
        super().__init__()
        self._ad_types: dict[int, ADTypeInfo] = {}
        self._ad_types_by_name: dict[str, ADTypeInfo] = {}

        try:
            self._load_ad_types()
        except (FileNotFoundError, OSError, msgspec.DecodeError, KeyError) as e:
            # Log warning if YAML loading fails, continue with empty registry
            logger.warning(
                "Failed to load AD types from YAML: %s. Registry will be empty.",
                e,
            )

    def _load_ad_types(self) -> None:
        """Load AD types from YAML file."""
        base_path = find_bluetooth_sig_core_path()
        if not base_path:
            logger.warning("Bluetooth SIG core path not found. AD types registry will be empty.")
            return

        yaml_path = base_path / "ad_types.yaml"
        if not yaml_path.exists():
            logger.warning(
                "AD types YAML file not found at %s. Registry will be empty.",
                yaml_path,
            )
            return

        with yaml_path.open("r", encoding="utf-8") as f:
            data = msgspec.yaml.decode(f.read())

        if not data or "ad_types" not in data:
            logger.warning("Invalid AD types YAML format. Registry will be empty.")
            return

        for item in data["ad_types"]:
            value = item.get("value")
            name = item.get("name")
            reference = item.get("reference")

            if value is None or not name:
                continue

            # Handle hex values in YAML (e.g., 0x01)
            if isinstance(value, str):
                value = int(value, 16)

            ad_type_info = ADTypeInfo(
                value=value,
                name=name,
                reference=reference,
            )

            self._ad_types[value] = ad_type_info
            self._ad_types_by_name[name.lower()] = ad_type_info

        logger.info("Loaded %d AD types from specification", len(self._ad_types))

    def get_ad_type_info(self, ad_type: int) -> ADTypeInfo | None:
        """Get AD type info by value.

        Args:
            ad_type: The AD type value (e.g., 0x01 for Flags)

        Returns:
            ADTypeInfo object, or None if not found
        """
        with self._lock:
            return self._ad_types.get(ad_type)

    def get_ad_type_by_name(self, name: str) -> ADTypeInfo | None:
        """Get AD type info by name.

        Args:
            name: AD type name (case-insensitive)

        Returns:
            ADTypeInfo object, or None if not found
        """
        with self._lock:
            return self._ad_types_by_name.get(name.lower())

    def is_known_ad_type(self, ad_type: int) -> bool:
        """Check if AD type is known.

        Args:
            ad_type: The AD type value to check

        Returns:
            True if the AD type is registered, False otherwise
        """
        with self._lock:
            return ad_type in self._ad_types

    def get_all_ad_types(self) -> dict[int, ADTypeInfo]:
        """Get all registered AD types.

        Returns:
            Dictionary mapping AD type values to ADTypeInfo objects
        """
        with self._lock:
            return self._ad_types.copy()


# Global singleton instance
ad_types_registry = ADTypesRegistry()
