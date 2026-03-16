"""Value utilities for consumers of parsed Bluetooth SIG data.

Provides helpers that avoid leaking implementation details (msgspec,
enum ordering) into every consumer codebase.
"""

from __future__ import annotations

import enum
from typing import Any

import msgspec


def is_struct_value(obj: object) -> bool:
    """Check whether *obj* is a parsed struct produced by the library.

    Use this instead of ``hasattr(obj, '__struct_fields__')`` so consumer
    code does not depend on the msgspec implementation detail.

    Args:
        obj: Any parsed characteristic value.

    Returns:
        ``True`` if *obj* is a ``msgspec.Struct`` instance.

    """
    return isinstance(obj, msgspec.Struct)


def to_primitive(value: Any) -> int | float | str | bool:  # noqa: ANN401
    """Coerce a parsed characteristic value to a plain Python primitive.

    Handles the full range of types the library may return
    (``bool``, ``IntFlag``, ``IntEnum``, ``Enum``, ``int``, ``float``,
    ``str``, ``datetime``, ``timedelta``, msgspec Structs, …).

    **Order matters:**

    * ``bool`` before ``int`` — ``bool`` is a subclass of ``int``.
    * ``IntFlag`` before the ``.name`` branch — bit-field values expose
      a ``.name`` attribute but should be stored as a plain ``int``.
    * ``IntEnum`` / ``Enum`` → ``.name`` string.

    Args:
        value: Any value returned by ``BaseCharacteristic.parse_value()``
            or extracted from a struct field.

    Returns:
        A plain ``int``, ``float``, ``str``, or ``bool``.

    """
    if isinstance(value, bool):
        return value
    if isinstance(value, enum.IntFlag):
        return int(value)
    if (name := getattr(value, "name", None)) is not None:
        return str(name)
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        return value
    if isinstance(value, str):
        return value
    return str(value)
