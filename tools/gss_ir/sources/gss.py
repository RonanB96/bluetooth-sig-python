"""Read one GSS characteristic YAML file without interpreting phrases."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .errors import GssSourceError

STRUCT_TYPE = "struct"


@dataclass(frozen=True, kw_only=True)
class GssField:
    """One structure entry with its raw SIG strings."""

    field: str
    type_text: str
    size: str
    description: str


@dataclass(frozen=True, kw_only=True)
class GssNamedValue:
    """One raw ``value`` or ``bit`` entry from a GSS field table."""

    kind: str
    raw: str
    description: str


@dataclass(frozen=True, kw_only=True)
class GssValueTable:
    """Named codes or bits for one field, still as SIG text."""

    name: str
    entries: tuple[GssNamedValue, ...]


@dataclass(frozen=True, kw_only=True)
class GssCharacteristic:
    """Characteristic metadata and ordered structure fields."""

    identifier: str
    name: str
    description: str
    fields: tuple[GssField, ...]
    source_path: str
    value_tables: tuple[GssValueTable, ...] = ()


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


def _raw_token(value: object, location: str) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise GssSourceError(f"{location} must be text")
    return str(value).strip()


def _read_value_tables(body: dict[str, object]) -> tuple[GssValueTable, ...]:
    raw_fields = body.get("fields")
    if raw_fields is None:
        return ()
    if not isinstance(raw_fields, list):
        raise GssSourceError("fields must be a list")
    tables: list[GssValueTable] = []
    for index, entry in enumerate(raw_fields):
        if not isinstance(entry, dict):
            raise GssSourceError(f"fields entry {index} must be a mapping")
        values = entry.get("values")
        if values is None:
            continue
        if not isinstance(values, list):
            raise GssSourceError(f"fields entry {index} values must be a list")
        named: list[GssNamedValue] = []
        for value_index, item in enumerate(values):
            location = f"fields entry {index} value {value_index}"
            if not isinstance(item, dict):
                raise GssSourceError(f"{location} must be a mapping")
            has_bit = "bit" in item
            has_value = "value" in item
            if has_bit and has_value:
                raise GssSourceError(f"{location} has both bit and value")
            if not has_bit and not has_value:
                continue
            kind = "bit" if has_bit else "value"
            description = item.get("description", "")
            if description is None:
                description = ""
            if not isinstance(description, str):
                raise GssSourceError(f"{location} description must be text")
            named.append(
                GssNamedValue(
                    kind=kind,
                    raw=_raw_token(item["bit"] if has_bit else item["value"], location),
                    description=description.strip(),
                )
            )
        if named:
            tables.append(
                GssValueTable(
                    name=_require_text(entry.get("name"), f"fields entry {index} name"),
                    entries=tuple(named),
                )
            )
    return tuple(tables)


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
        value_tables=_read_value_tables(body),
    )
