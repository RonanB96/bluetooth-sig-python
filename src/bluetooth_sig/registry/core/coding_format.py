"""Coding Format registry for Bluetooth SIG audio codec definitions.

Used during LE Audio codec negotiation to identify codec types (LC3, mSBC, etc.)
in capability exchange and stream configuration.
"""

from __future__ import annotations

import logging

import msgspec

from bluetooth_sig.registry.base import BaseGenericRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path
from bluetooth_sig.types.registry.coding_format import CodingFormatInfo

logger = logging.getLogger(__name__)


class CodingFormatRegistry(BaseGenericRegistry[CodingFormatInfo]):
    """Registry for Bluetooth audio coding formats with lazy loading.

    This registry loads coding format definitions from the official Bluetooth SIG
    assigned_numbers YAML file, providing codec identification for LE Audio
    and Classic Audio profiles.

    Examples:
        >>> from bluetooth_sig.registry.core.coding_format import coding_format_registry
        >>> info = coding_format_registry.get_coding_format_info(0x06)
        >>> info.name
        'LC3'
    """

    def __init__(self) -> None:
        """Initialize the coding format registry."""
        super().__init__()
        self._coding_formats: dict[int, CodingFormatInfo] = {}
        self._coding_formats_by_name: dict[str, CodingFormatInfo] = {}

    def _load(self) -> None:
        """Perform the actual loading of coding format data."""
        base_path = find_bluetooth_sig_path()
        if not base_path:
            logger.warning("Bluetooth SIG path not found. Coding format registry will be empty.")
            self._loaded = True
            return

        yaml_path = base_path.parent / "core" / "coding_format.yaml"
        if not yaml_path.exists():
            logger.warning(
                "Coding format YAML file not found at %s. Registry will be empty.",
                yaml_path,
            )
            self._loaded = True
            return

        try:
            with yaml_path.open("r", encoding="utf-8") as f:
                data = msgspec.yaml.decode(f.read())

            if not data or "coding_formats" not in data:
                logger.warning("Invalid coding format YAML format. Registry will be empty.")
                self._loaded = True
                return

            for item in data["coding_formats"]:
                value = item.get("value")
                name = item.get("name")

                if value is None or not name:
                    continue

                # Handle hex values in YAML (e.g., 0x06)
                if isinstance(value, str):
                    value = int(value, 16)

                coding_format_info = CodingFormatInfo(
                    value=value,
                    name=name,
                )

                self._coding_formats[value] = coding_format_info
                self._coding_formats_by_name[name.lower()] = coding_format_info

            logger.info("Loaded %d coding formats from specification", len(self._coding_formats))
        except (FileNotFoundError, OSError, msgspec.DecodeError, KeyError) as e:
            logger.warning(
                "Failed to load coding formats from YAML: %s. Registry will be empty.",
                e,
            )

        self._loaded = True

    def get_coding_format_info(self, value: int) -> CodingFormatInfo | None:
        """Get coding format info by value (lazy loads on first call).

        Args:
            value: The coding format value (e.g., 0x06 for LC3)

        Returns:
            CodingFormatInfo object, or None if not found
        """
        self._ensure_loaded()
        with self._lock:
            return self._coding_formats.get(value)

    def get_coding_format_by_name(self, name: str) -> CodingFormatInfo | None:
        """Get coding format info by name (lazy loads on first call).

        Args:
            name: Coding format name (case-insensitive, e.g., "LC3", "mSBC")

        Returns:
            CodingFormatInfo object, or None if not found
        """
        self._ensure_loaded()
        with self._lock:
            return self._coding_formats_by_name.get(name.lower())

    def is_known_coding_format(self, value: int) -> bool:
        """Check if coding format is known (lazy loads on first call).

        Args:
            value: The coding format value to check

        Returns:
            True if the coding format is registered, False otherwise
        """
        self._ensure_loaded()
        with self._lock:
            return value in self._coding_formats

    def get_all_coding_formats(self) -> dict[int, CodingFormatInfo]:
        """Get all registered coding formats (lazy loads on first call).

        Returns:
            Dictionary mapping coding format values to CodingFormatInfo objects
        """
        self._ensure_loaded()
        with self._lock:
            return self._coding_formats.copy()


# Global singleton instance
coding_format_registry = CodingFormatRegistry()
