"""Authoritative registry prewarm catalogue.

The catalogue derives prewarm targets from registry base-class descendants,
then appends explicit outliers that do not follow the shared registry base
hierarchy.
"""

from __future__ import annotations

import functools
import importlib
import pkgutil
import re
from collections.abc import Callable
from typing import Any

from ..gatt.uuid_registry import get_uuid_registry
from ..registry.base import BaseGenericRegistry, BaseUUIDClassRegistry, BaseUUIDRegistry

_REGISTRY_PACKAGE_ROOT = "bluetooth_sig.registry"
# These modules host BaseUUIDClassRegistry descendants used by public APIs.
_EXTRA_DISCOVERY_MODULES: tuple[str, ...] = (
    "bluetooth_sig.gatt.characteristics.registry",
    "bluetooth_sig.gatt.services.registry",
)

RegistryLoader = tuple[str, Callable[[], Any]]


def _to_snake_case(name: str) -> str:
    """Convert CamelCase/PascalCase names to snake_case."""
    first_pass = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", first_pass).lower()


def _iter_subclasses(root: type[Any]) -> list[type[Any]]:
    """Return all recursive subclasses of *root* (excluding the root itself)."""
    discovered: list[type[Any]] = []
    stack = list(root.__subclasses__())
    seen: set[type[Any]] = set()

    while stack:
        cls = stack.pop()
        if cls in seen:
            continue
        seen.add(cls)
        discovered.append(cls)
        stack.extend(cls.__subclasses__())

    return discovered


def _import_registry_modules() -> None:
    """Import registry modules so subclass discovery has complete coverage."""
    registry_pkg = importlib.import_module(_REGISTRY_PACKAGE_ROOT)
    if hasattr(registry_pkg, "__path__"):
        for module_info in pkgutil.walk_packages(registry_pkg.__path__, f"{_REGISTRY_PACKAGE_ROOT}."):
            importlib.import_module(module_info.name)

    for module_name in _EXTRA_DISCOVERY_MODULES:
        importlib.import_module(module_name)


def _build_discovered_registry_loaders() -> tuple[RegistryLoader, ...]:
    """Build ensure-loaded loaders from registry base-class descendants."""
    _import_registry_modules()

    registry_classes: set[type[Any]] = set()
    registry_classes.update(_iter_subclasses(BaseGenericRegistry))
    registry_classes.update(_iter_subclasses(BaseUUIDRegistry))
    registry_classes.update(_iter_subclasses(BaseUUIDClassRegistry))

    loaders: list[RegistryLoader] = []
    for registry_cls in sorted(registry_classes, key=lambda cls: f"{cls.__module__}.{cls.__qualname__}"):
        loader_name = _to_snake_case(registry_cls.__name__.replace("Registry", "")) + "_registry"
        loader = registry_cls.get_instance().ensure_loaded
        loaders.append((loader_name, loader))

    return tuple(loaders)


def _build_outlier_loaders() -> tuple[RegistryLoader, ...]:
    """Build loaders for registries that do not use shared base registry classes."""
    return (("uuid_registry", lambda: get_uuid_registry().ensure_loaded()),)


@functools.lru_cache(maxsize=1)
def _cached_prewarm_loaders() -> tuple[RegistryLoader, ...]:
    """Build and cache the full prewarm loader list."""
    return _build_discovered_registry_loaders() + _build_outlier_loaders()


def get_prewarm_loaders() -> tuple[RegistryLoader, ...]:
    """Return cached prewarm loaders, building discovery state on first call."""
    return _cached_prewarm_loaders()
