"""Protocol definitions for Bluetooth SIG standards."""

from __future__ import annotations

from typing import Any, Protocol


class CharacteristicDataProtocol(Protocol):  # pylint: disable=too-few-public-methods
    """Minimal protocol describing the attributes used by parsers.

    This avoids importing the full `CharacteristicData` type here and
    gives callers a useful static type for `other_characteristics`.

    Now includes field-level error reporting and parse trace capabilities
    for improved diagnostics.
    """

    value: Any
    raw_data: bytes
    parse_success: bool
    properties: list[str]
    name: str
    field_errors: list[Any]  # ParseFieldError, but avoid circular import
    parse_trace: list[str]
