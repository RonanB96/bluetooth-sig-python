#!/usr/bin/env python3
"""Generate PEP 562 lazy export maps and type stubs for GATT packages."""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from importlib import import_module

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.registry_utils import ModuleDiscovery
from bluetooth_sig.gatt.services.base import BaseGattService

CHAR_PACKAGE = "bluetooth_sig.gatt.characteristics"
SVC_PACKAGE = "bluetooth_sig.gatt.services"
DESC_PACKAGE = "bluetooth_sig.gatt.descriptors"

CHAR_EXCLUSIONS = {
    "__init__",
    "__main__",
    "_export_map",
    "base",
    "registry",
    "templates",
    "pipeline",
    "characteristic_meta",
    "context_lookup",
    "descriptor_mixin",
    "role_classifier",
    "custom",
    "utils",
    "blood_pressure_common",
    "device_info",
    "fitness_machine_common",
}

SVC_EXCLUSIONS = {
    "__init__",
    "__main__",
    "_export_map",
    "base",
    "registry",
}

DESC_EXCLUSIONS = {
    "__init__",
    "__main__",
    "_export_map",
    "base",
    "registry",
}

CHAR_EXTRA_EXPORTS: dict[str, str] = {
    "UncertaintyData": f"{CHAR_PACKAGE}.uncertainty",
}


def _is_exportable_class(obj: object, module_name: str, base: type[object]) -> bool:
    if not inspect.isclass(obj):
        return False
    if obj.__module__ != module_name:
        return False
    if obj is base:
        return False
    if getattr(obj, "_is_template", False):
        return False
    if getattr(obj, "_is_base_class", False):
        return False
    return issubclass(obj, base)


def _discover_class_exports(
    package_name: str,
    exclusions: set[str],
    base: type[object],
    extra_exports: dict[str, str],
) -> dict[str, str]:
    module_names = ModuleDiscovery.iter_module_names(package_name, exclusions)
    export_map: dict[str, str] = dict(extra_exports)
    for module_name in module_names:
        module = import_module(module_name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if not _is_exportable_class(obj, module.__name__, base):
                continue
            export_map[obj.__name__] = module_name
    return dict(sorted(export_map.items()))


def _discover_descriptor_exports() -> dict[str, str]:
    from bluetooth_sig.gatt.descriptors.base import BaseDescriptor

    module_names = ModuleDiscovery.iter_module_names(DESC_PACKAGE, DESC_EXCLUSIONS)
    export_map: dict[str, str] = {}
    for module_name in module_names:
        module = import_module(module_name)
        for name, obj in inspect.getmembers(module):
            if name.startswith("_") or not inspect.isclass(obj):
                continue
            if obj.__module__ != module.__name__ or obj is BaseDescriptor:
                continue
            export_map[name] = module_name
    return dict(sorted(export_map.items()))


def _render_export_map(package_label: str, export_map: dict[str, str]) -> str:
    lines = [
        f'"""Generated lazy export map for {package_label}. Do not edit by hand."""',
        "",
        "from __future__ import annotations",
        "",
        "LAZY_EXPORT_MAP: dict[str, str] = {",
    ]
    for name, module_path in export_map.items():
        lines.append(f'    "{name}": "{module_path}",')
    lines.extend(
        [
            "}",
            "",
            "LAZY_EXPORT_NAMES: tuple[str, ...] = (",
        ]
    )
    for name in export_map:
        lines.append(f'    "{name}",')
    lines.extend([")", ""])
    return "\n".join(lines)


def _render_stub(export_map: dict[str, str], eager_imports: list[str], eager_names: list[str]) -> str:
    lines = ['"""Generated type stubs for lazy package exports. Do not edit by hand."""', ""]
    lines.extend(eager_imports)
    for name, module_path in export_map.items():
        relative = module_path.rsplit(".", 1)[-1]
        lines.append(f"from .{relative} import {name}")
    lines.append("")
    lines.append("__all__ = [")
    for name in eager_names:
        lines.append(f'    "{name}",')
    for name in export_map:
        lines.append(f'    "{name}",')
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def _write_package_artifacts(
    package_dir: Path,
    package_label: str,
    export_map: dict[str, str],
    eager_stub_imports: list[str],
    eager_names: list[str],
) -> None:
    export_path = package_dir / "_export_map.py"
    stub_path = package_dir / "__init__.pyi"
    export_path.write_text(_render_export_map(package_label, export_map), encoding="utf-8")
    stub_path.write_text(_render_stub(export_map, eager_stub_imports, eager_names), encoding="utf-8")
    print(f"Wrote {len(export_map)} exports to {export_path.relative_to(repo_root)}")


def main() -> None:
    char_map = _discover_class_exports(
        CHAR_PACKAGE,
        CHAR_EXCLUSIONS,
        BaseCharacteristic,
        CHAR_EXTRA_EXPORTS,
    )
    svc_map = _discover_class_exports(
        SVC_PACKAGE,
        SVC_EXCLUSIONS,
        BaseGattService,
        {},
    )
    desc_map = _discover_descriptor_exports()

    _write_package_artifacts(
        repo_root / "src/bluetooth_sig/gatt/characteristics",
        "GATT characteristics",
        char_map,
        [
            "from .base import BaseCharacteristic",
            "from .registry import CharacteristicName, CharacteristicRegistry, get_characteristic_class_map",
        ],
        [
            "BaseCharacteristic",
            "CharacteristicName",
            "CharacteristicRegistry",
            "get_characteristic_class_map",
        ],
    )
    _write_package_artifacts(
        repo_root / "src/bluetooth_sig/gatt/services",
        "GATT services",
        svc_map,
        [
            "from .base import (",
            "    CharacteristicStatus,",
            "    ServiceCharacteristicInfo,",
            "    ServiceCompletenessReport,",
            "    ServiceHealthStatus,",
            "    ServiceValidationResult,",
            ")",
            "from .registry import GattServiceRegistry, ServiceName, get_service_class_map",
        ],
        [
            "CharacteristicStatus",
            "GattServiceRegistry",
            "ServiceCharacteristicInfo",
            "ServiceCompletenessReport",
            "ServiceHealthStatus",
            "ServiceName",
            "ServiceValidationResult",
            "get_service_class_map",
        ],
    )
    _write_package_artifacts(
        repo_root / "src/bluetooth_sig/gatt/descriptors",
        "GATT descriptors",
        desc_map,
        [
            "from .base import BaseDescriptor",
            "from .registry import DescriptorRegistry",
        ],
        ["BaseDescriptor", "DescriptorRegistry"],
    )


if __name__ == "__main__":
    main()
