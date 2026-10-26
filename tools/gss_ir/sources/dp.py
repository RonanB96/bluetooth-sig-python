"""Read device-property YAML that names the characteristics it uses."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .errors import GssSourceError

_CHARACTERISTIC_PREFIX = "org.bluetooth.characteristic."


@dataclass(frozen=True, kw_only=True)
class DeviceProperty:
    """One device property and the characteristic ids it names."""

    identifier: str
    name: str
    group: str
    characteristics: tuple[str, ...]
    source_path: str


def _text(value: object, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GssSourceError(f"{location} must be text")
    return value.strip()


def _characteristic_ids(value: object, location: str) -> tuple[str, ...]:
    if isinstance(value, str):
        lines = tuple(line.strip() for line in value.splitlines() if line.strip())
    elif isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value):
        lines = tuple(item.strip() for item in value)
    else:
        raise GssSourceError(f"{location} must name at least one characteristic")
    if not lines:
        raise GssSourceError(f"{location} must name at least one characteristic")
    for identifier in lines:
        if not identifier.startswith(_CHARACTERISTIC_PREFIX):
            raise GssSourceError(f"{location} has characteristic id {identifier}")
    return lines


def read_device_property(path: Path, *, source_path: str) -> DeviceProperty:
    """Read one device-property document.

    Args:
        path: Property YAML file.
        source_path: Repository-relative path stored on the result.

    Returns:
        The property and the characteristic ids it names.

    Raises:
        GssSourceError: If the document has no property, name, group, or characteristic id.
        OSError: If the file cannot be read.
    """
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or not isinstance(loaded.get("property"), dict):
        raise GssSourceError(f"{source_path} has no property")
    body = loaded["property"]
    identifier = _text(body.get("identifier"), f"{source_path} identifier")
    return DeviceProperty(
        identifier=identifier,
        name=_text(body.get("name"), f"{identifier} name"),
        group=_text(body.get("group"), f"{identifier} group"),
        characteristics=_characteristic_ids(body.get("characteristic"), f"{identifier} characteristic"),
        source_path=source_path,
    )


def read_device_properties(directory: Path) -> tuple[DeviceProperty, ...]:
    """Read every device-property YAML file in a directory.

    Args:
        directory: Directory of ``org.bluetooth.property.*.yaml`` files.

    Returns:
        Properties in identifier order.

    Raises:
        GssSourceError: If a document is not a property, or an identifier repeats.
        OSError: If a file cannot be read.
    """
    found: dict[str, DeviceProperty] = {}
    for path in sorted(directory.glob("org.bluetooth.property.*.yaml")):
        source_path = path.as_posix()
        prop = read_device_property(path, source_path=source_path)
        if prop.identifier in found:
            raise GssSourceError(f"duplicate device property {prop.identifier}")
        found[prop.identifier] = prop
    return tuple(found[identifier] for identifier in sorted(found))
