"""Common utilities for GATT registries.

This module contains shared utility classes used by both characteristic and
service registries to avoid code duplication.
"""

from __future__ import annotations

import inspect
import pkgutil
from importlib import import_module
from typing import Any, Callable, TypeVar

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


T = TypeVar("T")


class ModuleDiscovery:
    """Base class for discovering classes in a package using pkgutil.walk_packages.

    This utility provides a common pattern for discovering and validating classes
    across different GATT packages (characteristics and services).
    """

    @staticmethod
    def iter_module_names(
        package_name: str,
        module_exclusions: set[str],
    ) -> list[str]:
        """Return sorted module names discovered via pkgutil.walk_packages.

        Args:
            package_name: Fully qualified package name (e.g., "bluetooth_sig.gatt.characteristics")
            module_exclusions: Set of module basenames to exclude (e.g., {"__init__", "base"})

        Returns:
            Sorted list of module names found in the package

        References:
            Python standard library documentation, pkgutil.walk_packages,
            https://docs.python.org/3/library/pkgutil.html#pkgutil.walk_packages
        """
        package = import_module(package_name)
        module_names: list[str] = []
        prefix = f"{package_name}."
        for module_info in pkgutil.walk_packages(package.__path__, prefix):
            module_basename = module_info.name.rsplit(".", 1)[-1]
            if module_basename in module_exclusions:
                continue
            module_names.append(module_info.name)
        module_names.sort()
        return module_names

    @staticmethod
    def discover_classes(
        module_names: list[str],
        base_class: type[T],
        validator: Callable[[Any], bool],
    ) -> list[type[T]]:
        """Discover all concrete classes in modules that pass validation.

        Args:
            module_names: List of module names to search
            base_class: Base class type for filtering
            validator: Function to validate if object is a valid subclass

        Returns:
            Sorted list of discovered classes
        """
        discovered: list[type[T]] = []
        for module_name in module_names:
            module = import_module(module_name)
            candidates: list[type[T]] = []
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if not validator(obj):
                    continue
                if obj is base_class or getattr(obj, "_is_template", False):
                    continue
                if obj.__module__ != module.__name__:
                    continue

                # Validate that the class has required methods
                if not hasattr(obj, "get_class_uuid") or not callable(obj.get_class_uuid):
                    continue  # Skip classes without proper UUID resolution

                candidates.append(obj)
            candidates.sort(key=lambda cls: cls.__name__)
            discovered.extend(candidates)
        return discovered
