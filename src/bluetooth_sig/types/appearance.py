"""Appearance value types for Bluetooth device identification."""

from __future__ import annotations

import msgspec


class AppearanceInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Decoded appearance information from registry.

    Attributes:
        category: Human-readable device category name (e.g., "Heart Rate Sensor")
        subcategory: Optional subcategory name (e.g., "Heart Rate Belt")
        category_value: Category value (upper 10 bits of appearance code)
        subcategory_value: Optional subcategory value (lower 6 bits of appearance code)
    """

    category: str
    subcategory: str | None = None
    category_value: int
    subcategory_value: int | None = None

    @property
    def full_name(self) -> str:
        """Get full appearance name.

        Returns:
            Full name with category and optional subcategory
            (e.g., "Heart Rate Sensor: Heart Rate Belt" or "Phone")
        """
        if self.subcategory:
            return f"{self.category}: {self.subcategory}"
        return self.category


class AppearanceData(msgspec.Struct, kw_only=True):
    """Appearance characteristic data with human-readable info.

    Attributes:
        raw_value: Raw 16-bit appearance code from BLE
        info: Optional decoded appearance information from registry
    """

    raw_value: int
    info: AppearanceInfo | None = None

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
        return self.info.subcategory if self.info else None

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
