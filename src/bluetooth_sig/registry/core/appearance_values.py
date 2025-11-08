"""Registry for Bluetooth appearance values.

This module provides a registry for looking up human-readable device types
and categories from appearance codes found in advertising data and GATT
characteristics.
"""

from __future__ import annotations

import threading
from pathlib import Path

import msgspec

from bluetooth_sig.registry.base import BaseRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path
from bluetooth_sig.types.appearance import AppearanceInfo


class AppearanceValuesRegistry(BaseRegistry[AppearanceInfo]):
    """Registry for Bluetooth appearance values with lazy loading.

    This registry loads appearance values from the Bluetooth SIG assigned_numbers
    YAML file and provides lookup methods to decode appearance codes into
    human-readable device type information.

    The registry uses lazy loading - the YAML file is only parsed on the first
    lookup call. This improves startup time and reduces memory usage when the
    registry is not needed.

    Thread Safety:
        This registry is thread-safe. Multiple threads can safely call
        get_appearance_info() concurrently.

    Example:
        >>> registry = AppearanceValuesRegistry()
        >>> info = registry.get_appearance_info(833)
        >>> if info:
        ...     print(info.full_name)  # "Heart Rate Sensor: Heart Rate Belt"
        ...     print(info.category)  # "Heart Rate Sensor"
        ...     print(info.subcategory)  # "Heart Rate Belt"
    """

    def __init__(self) -> None:
        """Initialize the registry with lazy loading."""
        super().__init__()
        self._appearances: dict[int, AppearanceInfo] = {}
        self._loaded = False
        self._lock = threading.RLock()

    def _ensure_loaded(self) -> None:
        """Lazy load appearance values from YAML on first access.

        This method is thread-safe and ensures the YAML is only loaded once,
        even when called concurrently from multiple threads.
        """
        if self._loaded:
            return

        with self._lock:
            # Double-check locking pattern: check again inside lock
            # NOTE: This pattern is correct but confuses mypy's reachability analysis
            if self._loaded:
                return

            base_path = find_bluetooth_sig_path()
            if not base_path:
                self._loaded = True
                return

            # Appearance values are in core/ directory, not uuids/
            yaml_path = base_path.parent / "core" / "appearance_values.yaml"
            if not yaml_path.exists():
                self._loaded = True
                return

            self._load_yaml(yaml_path)
            self._loaded = True

    def _load_yaml(self, yaml_path: Path) -> None:
        """Load and parse the appearance values YAML file.

        Args:
            yaml_path: Path to the appearance_values.yaml file
        """
        with yaml_path.open("r", encoding="utf-8") as f:
            data = msgspec.yaml.decode(f.read())

        if not data or not isinstance(data, dict):
            return

        appearance_values = data.get("appearance_values")
        if not isinstance(appearance_values, list):
            return

        for item in appearance_values:
            if not isinstance(item, dict):
                continue

            category_val = item.get("category")
            category_name = item.get("name")

            if category_val is None or not category_name:
                continue

            # Store category without subcategory
            # Appearance code = (category << 6) | subcategory
            # Category only: subcategory = 0
            appearance_code = category_val << 6
            self._appearances[appearance_code] = AppearanceInfo(
                category=category_name,
                subcategory=None,
                category_value=category_val,
                subcategory_value=None,
            )

            # Store subcategories if present
            subcategories = item.get("subcategory", [])
            if not isinstance(subcategories, list):
                continue

            for subcat in subcategories:
                if not isinstance(subcat, dict):
                    continue

                subcat_val = subcat.get("value")
                subcat_name = subcat.get("name")

                if subcat_val is None or not subcat_name:
                    continue

                # Full appearance code = (category << 6) | subcategory
                full_code = (category_val << 6) | subcat_val
                self._appearances[full_code] = AppearanceInfo(
                    category=category_name,
                    subcategory=subcat_name,
                    category_value=category_val,
                    subcategory_value=subcat_val,
                )

    def get_appearance_info(self, appearance_code: int) -> AppearanceInfo | None:
        """Get appearance info by appearance code.

        This method lazily loads the YAML file on first call.

        Args:
            appearance_code: 16-bit appearance value from BLE

        Returns:
            AppearanceInfo with decoded information, or None if code not found

        Example:
            >>> registry = AppearanceValuesRegistry()
            >>> info = registry.get_appearance_info(833)
            >>> if info:
            ...     print(info.full_name)  # "Heart Rate Sensor: Heart Rate Belt"
        """
        self._ensure_loaded()
        return self._appearances.get(appearance_code)


# Singleton instance for global use
appearance_values_registry = AppearanceValuesRegistry()
