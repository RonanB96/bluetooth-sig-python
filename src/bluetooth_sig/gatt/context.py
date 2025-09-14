"""Context objects used during characteristic parsing.

This module provides a small, well-typed container that parsers can use to
access device-level information, advertisement data, and already-parsed
characteristics when decoding values that depend on context.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol


class CharacteristicDataProtocol(Protocol):  # pylint: disable=too-few-public-methods
    """Minimal protocol describing the attributes used by parsers.

    This avoids importing the full `CharacteristicData` type here and gives
    callers a useful static type for `other_characteristics`.
    """

    value: Any
    raw_data: bytes | None
    parse_success: bool


@dataclass
class DeviceInfo:
    """Basic device metadata available to parsers."""

    address: str | None = None
    name: str | None = None
    manufacturer_data: dict[int, bytes] | None = None
    service_uuids: list[str] | None = None


@dataclass
class CharacteristicContext:
    """Runtime context passed into parsers.

    Attributes:
        device_info: Basic device metadata (address, name, manufacturer data).
        advertisement: Raw advertisement bytes if available.
        other_characteristics: Mapping from characteristic UUID string to
            previously-parsed characteristic result (typical value is
            `bluetooth_sig.core.CharacteristicData`). Parsers may consult this
            mapping to implement multi-characteristic decoding.
        raw_service: Optional raw service-level payload when applicable.
    """

    device_info: DeviceInfo | None = None
    advertisement: bytes | None = None
    # Mapping from characteristic UUID -> parsed result (minimal protocol).
    other_characteristics: Mapping[str, CharacteristicDataProtocol] | None = None
    raw_service: bytes | None = None
