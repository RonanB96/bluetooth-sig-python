"""Parse a 16-bit assigned number from SIG YAML."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .errors import GssSourceError

_UUID16_MAX = 0xFFFF


def parse_assigned_number(value: object, *, location: str) -> int:
    """Return a 16-bit assigned number.

    Args:
        value: YAML value, either an integer or a decimal or ``0x`` hex string.
        location: Diagnostic name of the value.

    Returns:
        Integer in the closed range 0 to 65535.

    Raises:
        GssSourceError: If the value is not a 16-bit assigned number.
    """
    if isinstance(value, bool):
        raise GssSourceError(f"{location} is not a 16-bit assigned number")
    if isinstance(value, int):
        number = value
    elif isinstance(value, str):
        token = value.strip()
        base = 16 if token.lower().startswith("0x") else 10
        try:
            number = int(token, base)
        except ValueError as error:
            raise GssSourceError(f"{location} is not a 16-bit assigned number") from error
    else:
        raise GssSourceError(f"{location} is not a 16-bit assigned number")
    if number < 0 or number > _UUID16_MAX:
        raise GssSourceError(f"{location} is outside the 16-bit range")
    return number


@dataclass(frozen=True, kw_only=True)
class AssignedUuid:
    """One assigned-number entry that still carries its display name."""

    identifier: str
    name: str
    uuid: int


def _load_uuid_entries(path: Path, *, key_name: str) -> list[dict[str, object]]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or not isinstance(loaded.get("uuids"), list):
        raise GssSourceError(f"{path.name} has no uuid list")
    entries: list[dict[str, object]] = []
    seen: set[str] = set()
    for index, entry in enumerate(loaded["uuids"]):
        if not isinstance(entry, dict):
            raise GssSourceError(f"{path.name} entry {index} must be a mapping")
        identifier = entry.get("id")
        if not isinstance(identifier, str) or not identifier:
            raise GssSourceError(f"{path.name} entry {index} has no id")
        if identifier in seen:
            raise GssSourceError(f"duplicate {key_name} for {identifier}")
        seen.add(identifier)
        entries.append(entry)
    return entries


def read_assigned_entries(path: Path, *, key_name: str) -> tuple[AssignedUuid, ...]:
    """Read an assigned-number YAML list, including each display name.

    Args:
        path: YAML file with a ``uuids`` list of ``id``, ``name``, and ``uuid`` entries.
        key_name: Diagnostic name used when an id repeats.

    Returns:
        Entries in file order.

    Raises:
        GssSourceError: If the file is not that list, an id repeats, or a name is missing.
        OSError: If the file cannot be read.
    """
    records: list[AssignedUuid] = []
    for entry in _load_uuid_entries(path, key_name=key_name):
        identifier = entry["id"]
        if not isinstance(identifier, str):
            raise GssSourceError(f"{path.name} entry has no id")
        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            raise GssSourceError(f"{identifier} has no name")
        records.append(
            AssignedUuid(
                identifier=identifier,
                name=name.strip(),
                uuid=parse_assigned_number(entry.get("uuid"), location=f"{identifier} uuid"),
            )
        )
    return tuple(records)


def read_assigned_uuids(path: Path, *, key_name: str) -> dict[str, int]:
    """Read an assigned-number YAML list.

    Args:
        path: YAML file with a ``uuids`` list of ``id`` and ``uuid`` entries.
        key_name: Diagnostic name used when an id repeats.

    Returns:
        Mapping of identifier to a 16-bit UUID.

    Raises:
        GssSourceError: If the file is not that list, or an id repeats.
        OSError: If the file cannot be read.
    """
    found: dict[str, int] = {}
    for entry in _load_uuid_entries(path, key_name=key_name):
        identifier = entry["id"]
        if not isinstance(identifier, str):
            raise GssSourceError(f"{path.name} entry has no id")
        found[identifier] = parse_assigned_number(entry.get("uuid"), location=f"{identifier} uuid")
    return found
