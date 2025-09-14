"""Context objects used during characteristic parsing."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from .protocols import CharacteristicDataProtocol


@dataclass
class DeviceInfo:
    """Basic device metadata available to parsers."""

    address: str = ""
    name: str = ""
    manufacturer_data: dict[int, bytes] = field(default_factory=dict)
    service_uuids: list[str] = field(default_factory=list)


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
    raw_service: bytes = b""
