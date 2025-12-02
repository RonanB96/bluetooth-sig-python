"""Appearance value types for Bluetooth device identification."""

from __future__ import annotations

import msgspec

from bluetooth_sig.registry.core.appearance_values import appearance_values_registry
from bluetooth_sig.types.registry.appearance_info import AppearanceInfo


class AppearanceData(msgspec.Struct, frozen=True, kw_only=True):
    """Appearance characteristic data with human-readable info.

    Attributes:
        raw_value: Raw 16-bit appearance code from BLE
        info: Optional decoded appearance information from registry
    """

    raw_value: int
    info: AppearanceInfo | None = None

    @classmethod
    def from_category(cls, category: str, subcategory: str | None = None) -> AppearanceData:
        """Create AppearanceData from category and subcategory strings.

        This helper validates the strings and finds the correct raw_value by
        searching the registry. Useful when creating appearance data from
        user-provided human-readable names.

        Args:
            category: Device category name (e.g., "Heart Rate Sensor")
            subcategory: Optional subcategory name (e.g., "Heart Rate Belt")

        Returns:
            AppearanceData with validated info and correct raw_value

        Raises:
            ValueError: If category/subcategory combination is not found in registry

        Example:
            >>> data = AppearanceData.from_category("Heart Rate Sensor", "Heart Rate Belt")
            >>> data.raw_value
            833
        """
        # Use public method to find appearance info
        info = appearance_values_registry.find_by_category_subcategory(category, subcategory)

        if info is None:
            # If not found, raise error
            if subcategory:
                raise ValueError(f"Unknown appearance: {category}: {subcategory}")
            raise ValueError(f"Unknown appearance: {category}")

        # Calculate raw_value from category and subcategory values
        subcategory_value = info.subcategory.value if info.subcategory else 0
        raw_value = (info.category_value << 6) | subcategory_value
        return cls(raw_value=raw_value, info=info)

    @property
    def category(self) -> str | None:
        """Get device category name.

        Returns:
            Category name or None if info not available
        """
        return self.info.category if self.info else None

    @property
    def subcategory(self) -> str | None:
        """Get device subcategory name.

        Returns:
            Subcategory name or None if not available
        """
        if self.info and self.info.subcategory:
            return self.info.subcategory.name
        return None

    @property
    def full_name(self) -> str | None:
        """Get full human-readable name.

        Returns:
            Full device type name or None if info not available
        """
        return self.info.full_name if self.info else None

    def __int__(self) -> int:
        """Allow casting to int for backward compatibility.

        Returns:
            Raw appearance value as integer
        """
        return self.raw_value

    def __format__(self, format_spec: str) -> str:
        """Format appearance value for backward compatibility.

        Supports hex formatting for backward compatibility with code that
        used raw int appearance values: f"{appearance:04X}"

        Args:
            format_spec: Format specification (e.g., "04X" for zero-padded uppercase hex)

        Returns:
            Formatted raw_value as string

        Example:
            >>> data = AppearanceData(raw_value=833, info=None)
            >>> f"{data:04X}"
            '0341'
        """
        return format(self.raw_value, format_spec)
