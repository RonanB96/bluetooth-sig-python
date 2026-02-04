"""Registry for Bluetooth appearance values.

This module provides a registry for looking up human-readable device types
and categories from appearance codes found in advertising data and GATT
characteristics.
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

import msgspec

from bluetooth_sig.gatt.constants import UINT16_MAX
from bluetooth_sig.registry.base import BaseGenericRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path
from bluetooth_sig.types.registry.appearance_info import AppearanceInfo, AppearanceSubcategoryInfo


class AppearanceValuesRegistry(BaseGenericRegistry[AppearanceInfo]):
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

    Example::
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

    def _load(self) -> None:
        """Perform the actual loading of appearance values data."""
        # Get path to uuids/ directory
        uuids_path = find_bluetooth_sig_path()
        if not uuids_path:
            self._loaded = True
            return

        # Appearance values are in core/ directory (sibling of uuids/)
        # Navigate from uuids/ to assigned_numbers/ then to core/
        assigned_numbers_path = uuids_path.parent
        yaml_path = assigned_numbers_path / "core" / "appearance_values.yaml"
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

            category_val: int | None = item.get("category")
            category_name: str | None = item.get("name")

            if category_val is None or not category_name:
                continue

            # Store category without subcategory
            # Appearance code = (category << 6) | subcategory
            # Category only: subcategory = 0
            appearance_code = category_val << 6
            self._appearances[appearance_code] = AppearanceInfo(
                category=category_name,
                category_value=category_val,
                subcategory=None,
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
                    category_value=category_val,
                    subcategory=AppearanceSubcategoryInfo(name=subcat_name, value=subcat_val),
                )

    def get_appearance_info(self, appearance_code: int) -> AppearanceInfo | None:
        """Get appearance info by appearance code.

        This method lazily loads the YAML file on first call.

        Args:
            appearance_code: 16-bit appearance value from BLE (0-65535)

        Returns:
            AppearanceInfo with decoded information, or None if code not found

        Raises:
            ValueError: If appearance_code is outside valid range (0-65535)

        Example::
            >>> registry = AppearanceValuesRegistry()
            >>> info = registry.get_appearance_info(833)
            >>> if info:
            ...     print(info.full_name)  # "Heart Rate Sensor: Heart Rate Belt"
        """
        # Validate input range for 16-bit appearance code
        if not 0 <= appearance_code <= UINT16_MAX:
            raise ValueError(f"Appearance code must be in range 0-{UINT16_MAX}, got {appearance_code}")

        self._ensure_loaded()
        return self._appearances.get(appearance_code)

    def find_by_category_subcategory(self, category: str, subcategory: str | None = None) -> AppearanceInfo | None:
        """Find appearance info by category and subcategory names.

        This method searches the registry for an appearance that matches
        the given category and subcategory names.

        Args:
            category: Device category name (e.g., "Heart Rate Sensor")
            subcategory: Optional subcategory name (e.g., "Heart Rate Belt")

        Returns:
            AppearanceInfo if found, None otherwise

        Example::
            >>> registry = AppearanceValuesRegistry()
            >>> info = registry.find_by_category_subcategory("Heart Rate Sensor", "Heart Rate Belt")
            >>> if info:
            ...     print(info.category_value)  # Category value for lookup
        """
        self._ensure_loaded()

        # Search for matching appearance
        for info in self._appearances.values():
            # Check category match
            if info.category != category:
                continue
            # Check subcategory match
            if subcategory is None and info.subcategory is None:
                return info
            if info.subcategory and info.subcategory.name == subcategory:
                return info

        return None


# Singleton instance for global use
appearance_values_registry = cast("AppearanceValuesRegistry", AppearanceValuesRegistry.get_instance())
