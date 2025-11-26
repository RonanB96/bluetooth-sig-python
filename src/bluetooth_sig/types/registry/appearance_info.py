"""Appearance information data structures.

This module contains only the data structures for appearance values,
with no dependencies on the registry system. This allows the registry
to import these types without creating circular dependencies.
"""

from __future__ import annotations

import msgspec


class AppearanceSubcategoryInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Decoded appearance subcategory information.

    Attributes:
        name: Human-readable subcategory name (e.g., "Heart Rate Belt")
        value: Subcategory value (0-63)
    """

    name: str
    value: int


class AppearanceInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Decoded appearance information from registry.

    The 16-bit appearance value encodes device type information:
    - Bits 15-6 (10 bits): Category value (0-1023)
    - Bits 5-0 (6 bits): Subcategory value (0-63)
    - Full code = (category << 6) | subcategory

    Attributes:
        category: Human-readable device category name (e.g., "Heart Rate Sensor")
        subcategory: Optional subcategory name (e.g., "Heart Rate Belt")
        category_value: Category value (upper 10 bits of appearance code)
        subcategory_value: Optional subcategory value (lower 6 bits of appearance code)
    """

    category: str
    category_value: int
    subcategories: list[AppearanceSubcategoryInfo] | None = None

    @property
    def full_name(self) -> str:
        """Get full appearance name.

        Returns:
            Full name with category and optional subcategory
            (e.g., "Heart Rate Sensor: Heart Rate Belt" or "Phone")
        """
        if self.subcategories:
            subcategory_names = ", ".join(sub.name for sub in self.subcategories)
            return f"{self.category}: {subcategory_names}"
        return self.category
