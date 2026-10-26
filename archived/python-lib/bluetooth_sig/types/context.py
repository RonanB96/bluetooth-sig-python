"""Context objects used during characteristic parsing."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import msgspec

from .company import ManufacturerData
from .registry.descriptor_types import DescriptorData
from .uuid import BluetoothUUID


class DeviceInfo(msgspec.Struct, kw_only=True):
    """Basic device metadata available to parsers."""

    address: str = ""
    name: str = ""
    manufacturer_data: dict[int, ManufacturerData] = msgspec.field(default_factory=dict)
    service_uuids: list[BluetoothUUID] = msgspec.field(default_factory=list)


class CharacteristicContext(msgspec.Struct, kw_only=True):
    """Runtime context passed into parsers - INPUT only.

    This provides the parsing context (device info, other characteristics for
    dependencies, etc.) but does NOT contain output fields. Descriptors have
    their own separate parsing flow.

    Attributes:
        device_info: Basic device metadata (address, name, manufacturer data).
        advertisement: Raw advertisement bytes if available.
        other_characteristics: Mapping from characteristic UUID string to
            previously-parsed characteristic result. Parsers may consult this
            mapping to implement multi-characteristic decoding.
        descriptors: Mapping from descriptor UUID string to parsed descriptor data.
            Provides access to characteristic descriptors during parsing.
        raw_service: Optional raw service-level payload when applicable.
        validate: Whether to perform validation during parsing (range checks, etc.).

    """

    device_info: DeviceInfo | None = None
    advertisement: bytes = b""
    other_characteristics: Mapping[str, Any] | None = None
    descriptors: Mapping[str, DescriptorData] | None = None
    raw_service: bytes = b""
    validate: bool = True
