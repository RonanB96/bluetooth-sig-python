from __future__ import annotations

import msgspec


class FieldSpec(msgspec.Struct, frozen=True):
    """Specification for a field in a characteristic structure."""

    field: str
    type: str
    size: str
    description: str


class CharacteristicSpec(msgspec.Struct, frozen=True):
    """Specification for a Bluetooth SIG characteristic from GSS."""

    identifier: str
    name: str
    description: str
    structure: list[FieldSpec]


class GssCharacteristicData(msgspec.Struct):
    """Top-level data structure for GSS characteristic YAML files."""

    characteristic: CharacteristicSpec
