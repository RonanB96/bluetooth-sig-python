"""Descriptor context utility functions.

Provides helper functions for extracting and working with descriptor information
from CharacteristicContext. These functions serve as both standalone utilities
and are mirrored as methods in BaseCharacteristic for convenience.
"""

from __future__ import annotations

from typing import Any

from ..types import DescriptorData
from .context import CharacteristicContext
from .descriptors.base import BaseDescriptor
from .descriptors.characteristic_presentation_format import (
    CharacteristicPresentationFormatData,
    CharacteristicPresentationFormatDescriptor,
)
from .descriptors.characteristic_user_description import CharacteristicUserDescriptionDescriptor
from .descriptors.valid_range import ValidRangeDescriptor


def get_descriptors_from_context(ctx: CharacteristicContext | None) -> dict[str, Any]:
    """Extract descriptor data from the parsing context.

    Args:
        ctx: The characteristic context containing descriptor information

    Returns:
        Dictionary mapping descriptor UUIDs to DescriptorData objects
    """
    if not ctx or not ctx.descriptors:
        return {}
    return dict(ctx.descriptors)


def get_descriptor_from_context(
    ctx: CharacteristicContext | None, descriptor_class: type[BaseDescriptor]
) -> DescriptorData | None:
    """Get a specific descriptor from context.

    Args:
        ctx: Characteristic context containing descriptors
        descriptor_class: Descriptor class to look for

    Returns:
        DescriptorData if found, None otherwise
    """
    if not ctx or not ctx.descriptors:
        return None

    try:
        descriptor_instance = descriptor_class()
        descriptor_uuid = str(descriptor_instance.uuid)
    except (ValueError, TypeError, AttributeError):
        return None

    return ctx.descriptors.get(descriptor_uuid)


def get_valid_range_from_context(ctx: CharacteristicContext | None = None) -> tuple[int | float, int | float] | None:
    """Get valid range from descriptor context if available.

    Args:
        ctx: Characteristic context containing descriptors

    Returns:
        Tuple of (min, max) values if Valid Range descriptor present, None otherwise
    """
    descriptor_data = get_descriptor_from_context(ctx, ValidRangeDescriptor)
    if descriptor_data and descriptor_data.value:
        return descriptor_data.value.min_value, descriptor_data.value.max_value
    return None


def get_presentation_format_from_context(
    ctx: CharacteristicContext | None = None,
) -> CharacteristicPresentationFormatData | None:
    """Get presentation format from descriptor context if available.

    Args:
        ctx: Characteristic context containing descriptors

    Returns:
        CharacteristicPresentationFormatData if present, None otherwise
    """
    descriptor_data = get_descriptor_from_context(ctx, CharacteristicPresentationFormatDescriptor)
    if descriptor_data and descriptor_data.value:
        return descriptor_data.value  # type: ignore[no-any-return]
    return None


def get_user_description_from_context(ctx: CharacteristicContext | None = None) -> str | None:
    """Get user description from descriptor context if available.

    Args:
        ctx: Characteristic context containing descriptors

    Returns:
        User description string if present, None otherwise
    """
    descriptor_data = get_descriptor_from_context(ctx, CharacteristicUserDescriptionDescriptor)
    if descriptor_data and descriptor_data.value:
        return descriptor_data.value.description  # type: ignore[no-any-return]
    return None


def validate_value_against_descriptor_range(value: int | float, ctx: CharacteristicContext | None = None) -> bool:
    """Validate a value against descriptor-defined valid range.

    Args:
        value: Value to validate
        ctx: Characteristic context containing descriptors

    Returns:
        True if value is within valid range or no range defined, False otherwise
    """
    valid_range = get_valid_range_from_context(ctx)
    if valid_range is None:
        return True
    min_val, max_val = valid_range
    return min_val <= value <= max_val


def enhance_error_message_with_descriptors(base_message: str, ctx: CharacteristicContext | None = None) -> str:
    """Enhance error message with descriptor information for better debugging.

    Args:
        base_message: Original error message
        ctx: Characteristic context containing descriptors

    Returns:
        Enhanced error message with descriptor context
    """
    enhancements: list[str] = []

    valid_range = get_valid_range_from_context(ctx)
    if valid_range:
        min_val, max_val = valid_range
        enhancements.append(f"Valid range: {min_val}-{max_val}")

    user_desc = get_user_description_from_context(ctx)
    if user_desc:
        enhancements.append(f"Description: {user_desc}")

    pres_format = get_presentation_format_from_context(ctx)
    if pres_format:
        enhancements.append(f"Format: {pres_format.format} ({pres_format.unit})")

    if enhancements:
        return f"{base_message} ({'; '.join(enhancements)})"
    return base_message
