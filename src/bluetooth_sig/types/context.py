"""Context objects used during characteristic parsing."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import cast

from .protocols import CharacteristicDataProtocol


@dataclass
class DeviceInfo:
    """Basic device metadata available to parsers."""

    address: str = ""
    name: str = ""
    manufacturer_data: dict[int, bytes] = field(default_factory=lambda: cast(dict[int, bytes], {}))
    service_uuids: list[str] = field(default_factory=lambda: cast(list[str], []))


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
    advertisement: bytes = b""
    other_characteristics: Mapping[str, CharacteristicDataProtocol] | None = None
    raw_service: bytes = b""

    def get_characteristic_by_uuid(self, uuid: str) -> CharacteristicDataProtocol | None:
        """Get another characteristic from the same service by UUID.

        Args:
            uuid: Short UUID (e.g., "2A34") or full UUID

        Returns:
            Parsed characteristic data if available, None otherwise
        """
        if not self.other_characteristics:
            return None
        return self.other_characteristics.get(uuid)

    def get_all_characteristics(self) -> dict[str, CharacteristicDataProtocol]:
        """Get all characteristics from the service.

        Returns:
            Dictionary mapping UUIDs to parsed characteristic data
        """
        if not self.other_characteristics:
            return {}
        return dict(self.other_characteristics)
