"""Common utilities for GATT registries.

This module contains shared utility classes used by both characteristic and
service registries to avoid code duplication.
"""

from __future__ import annotations

from typing_extensions import TypeGuard


class TypeValidator:  # pylint: disable=too-few-public-methods
    """Utility class for type validation operations.

    Note: Utility class pattern with static methods - pylint disable justified.
    """

    @staticmethod
    def is_subclass_of(candidate: object, base_class: type) -> TypeGuard[type]:
        """Return True when candidate is a subclass of base_class.

        Args:
            candidate: Object to check
            base_class: Base class to check against

        Returns:
            True if candidate is a subclass of base_class
        """
        return isinstance(candidate, type) and issubclass(candidate, base_class)
