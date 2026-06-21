"""PEP 562 lazy export helpers for GATT package barrels."""

from __future__ import annotations

import sys
from importlib import import_module


def lazy_getattr(package_name: str, export_map: dict[str, str], name: str) -> object:
    """Resolve and cache a lazily exported name from *export_map*.

    Args:
        package_name: Fully qualified package name (for caching and errors).
        export_map: Mapping of export name to fully qualified module path.
        name: Attribute name requested via ``__getattr__``.

    Returns:
        The resolved export.

    Raises:
        AttributeError: If *name* is not in *export_map*.
    """
    module_path = export_map.get(name)
    if module_path is None:
        msg = f"module {package_name!r} has no attribute {name!r}"
        raise AttributeError(msg)
    module = import_module(module_path)
    value = getattr(module, name)
    setattr(sys.modules[package_name], name, value)
    return value
