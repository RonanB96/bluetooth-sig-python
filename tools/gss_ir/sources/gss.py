"""Read one GSS characteristic YAML file without interpreting phrases."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .errors import GssSourceError


@dataclass(frozen=True, kw_only=True)
class GssField:
    """One structure entry with its raw SIG strings."""

    field: str
    type_text: str
    size: str
    description: str


@dataclass(frozen=True, kw_only=True)
class GssCharacteristic:
    """Characteristic metadata and ordered structure fields."""

    identifier: str
    name: str
    description: str
    fields: tuple[GssField, ...]
    source_path: str


def _require_text(value: object, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GssSourceError(f"{location} must be text")
    return value.strip()


def _raw_size(value: object) -> str:
    if isinstance(value, bool):
        raise GssSourceError("field size must be text")
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return value.strip()
    raise GssSourceError("field size must be text")


def _read_field(value: object, index: int) -> GssField:
    if not isinstance(value, dict):
        raise GssSourceError(f"structure entry {index} must be a mapping")
    description = value.get("description", "")
    if description is None:
        description = ""
    if not isinstance(description, str):
        raise GssSourceError(f"structure entry {index} description must be text")
    return GssField(
        field=_require_text(value.get("field"), f"structure entry {index} field"),
        type_text=_require_text(value.get("type"), f"structure entry {index} type"),
        size=_raw_size(value.get("size")),
        description=description.strip(),
    )


def read_characteristic(path: Path, *, source_path: str) -> GssCharacteristic:
    """Decode one characteristic file to identifier, name, description, and fields.

    Args:
        path: Filesystem path of the YAML file.
        source_path: Repository-relative path recorded with the document.

    Returns:
        Raw characteristic structure. Field phrases are not interpreted.

    Raises:
        GssSourceError: If the file is not one characteristic mapping.
        OSError: If the file cannot be read.
    """
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or not isinstance(loaded.get("characteristic"), dict):
        raise GssSourceError(f"{source_path} has no characteristic mapping")
    body = loaded["characteristic"]
    structure = body.get("structure")
    if not isinstance(structure, list) or not structure:
        raise GssSourceError(f"{source_path} has no structure")
    return GssCharacteristic(
        identifier=_require_text(body.get("identifier"), "identifier"),
        name=_require_text(body.get("name"), "name"),
        description=_require_text(body.get("description"), "description"),
        fields=tuple(_read_field(entry, index) for index, entry in enumerate(structure)),
        source_path=source_path,
    )
