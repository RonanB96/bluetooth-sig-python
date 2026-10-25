#!/usr/bin/env python3
"""Generate PEP 562 lazy export maps and type stubs for GATT packages."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

# ruff: noqa: E402
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.gatt.descriptors.base import BaseDescriptor
from bluetooth_sig.gatt.descriptors.registry import DescriptorRegistry
from bluetooth_sig.gatt.registry_utils import ModuleDiscovery
from bluetooth_sig.gatt.services.base import BaseGattService
from bluetooth_sig.gatt.services.registry import GattServiceRegistry


@dataclass(frozen=True, slots=True)
class LazyPackageConfig:
    """Configuration for one lazy-export GATT package."""

    relative_dir: str
    label: str
    package_name: str
    module_exclusions: frozenset[str]
    base_class: type[object]
    eager_stub_imports: dict[str, tuple[str, ...]]
    eager_export_names: tuple[str, ...]


PACKAGES: tuple[LazyPackageConfig, ...] = (
    LazyPackageConfig(
        relative_dir="src/bluetooth_sig/gatt/characteristics",
        label="GATT characteristics",
        package_name="bluetooth_sig.gatt.characteristics",
        module_exclusions=frozenset(CharacteristicRegistry._MODULE_EXCLUSIONS),
        base_class=BaseCharacteristic,
        eager_stub_imports={
            "base": ("BaseCharacteristic",),
            "registry": ("CharacteristicName", "CharacteristicRegistry", "get_characteristic_class_map"),
        },
        eager_export_names=(
            "BaseCharacteristic",
            "CharacteristicName",
            "CharacteristicRegistry",
            "get_characteristic_class_map",
        ),
    ),
    LazyPackageConfig(
        relative_dir="src/bluetooth_sig/gatt/services",
        label="GATT services",
        package_name="bluetooth_sig.gatt.services",
        module_exclusions=frozenset(GattServiceRegistry._MODULE_EXCLUSIONS),
        base_class=BaseGattService,
        eager_stub_imports={
            "base": (
                "CharacteristicStatus",
                "ServiceCharacteristicInfo",
                "ServiceCompletenessReport",
                "ServiceHealthStatus",
                "ServiceValidationResult",
            ),
            "registry": ("GattServiceRegistry", "ServiceName", "get_service_class_map"),
        },
        eager_export_names=(
            "CharacteristicStatus",
            "GattServiceRegistry",
            "ServiceCharacteristicInfo",
            "ServiceCompletenessReport",
            "ServiceHealthStatus",
            "ServiceName",
            "ServiceValidationResult",
            "get_service_class_map",
        ),
    ),
    LazyPackageConfig(
        relative_dir="src/bluetooth_sig/gatt/descriptors",
        label="GATT descriptors",
        package_name="bluetooth_sig.gatt.descriptors",
        module_exclusions=frozenset(DescriptorRegistry._MODULE_EXCLUSIONS),
        base_class=BaseDescriptor,
        eager_stub_imports={
            "base": ("BaseDescriptor",),
            "registry": ("DescriptorRegistry",),
        },
        eager_export_names=("BaseDescriptor", "DescriptorRegistry"),
    ),
)


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
    lines.extend(["}", ""])
    return "\n".join(lines)


def _build_stub_imports(
    export_map: dict[str, str],
    eager_stub_imports: dict[str, tuple[str, ...]],
) -> dict[str, list[str]]:
    imports: dict[str, list[str]] = {module: list(names) for module, names in eager_stub_imports.items()}
    for name, module_path in export_map.items():
        relative = module_path.rsplit(".", 1)[-1]
        bucket = imports.setdefault(relative, [])
        if name not in bucket:
            bucket.append(name)
    return imports


def _render_stub(
    export_map: dict[str, str],
    config: LazyPackageConfig,
) -> str:
    lines = ['"""Generated type stubs for lazy package exports. Do not edit by hand."""', ""]
    imports_by_module = _build_stub_imports(export_map, config.eager_stub_imports)
    for module, names in imports_by_module.items():
        joined = ", ".join(names)
        lines.append(f"from .{module} import {joined}")
    lines.append("")
    lines.append("__all__ = [")
    for name in config.eager_export_names:
        lines.append(f'    "{name}",')
    for name in export_map:
        lines.append(f'    "{name}",')
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def _apply_ruff_format(paths: list[Path]) -> None:
    """Format generated artifacts to match project ruff/isort settings."""
    if not paths:
        return
    path_args = [str(path) for path in paths]
    subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--fix", "-q", *path_args],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "ruff", "format", "-q", *path_args],
        cwd=repo_root,
        check=True,
    )


def _write_package_artifacts(config: LazyPackageConfig) -> None:
    package_dir = repo_root / config.relative_dir
    export_map = ModuleDiscovery.build_lazy_export_map(
        config.package_name,
        set(config.module_exclusions),
        config.base_class,
    )
    export_path = package_dir / "_export_map.py"
    stub_path = package_dir / "__init__.pyi"
    export_path.write_text(_render_export_map(config.label, export_map), encoding="utf-8")
    stub_path.write_text(_render_stub(export_map, config), encoding="utf-8")
    _apply_ruff_format([export_path, stub_path])
    print(f"Wrote {len(export_map)} exports to {export_path.relative_to(repo_root)}")


def main() -> None:
    """Discover GATT exports and write lazy export maps plus type stubs."""
    for config in PACKAGES:
        _write_package_artifacts(config)


if __name__ == "__main__":
    main()
