"""Protocol definitions for the device subsystem."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Protocol

from ..gatt.characteristics import CharacteristicName
from ..gatt.context import CharacteristicContext
from ..gatt.services import ServiceName
from ..types.uuid import BluetoothUUID


class SIGTranslatorProtocol(Protocol):  # pylint: disable=too-few-public-methods
    """Protocol for SIG translator interface."""

    @abstractmethod
    def parse_characteristics(
        self,
        char_data: dict[str, bytes],
        ctx: CharacteristicContext | None = None,
    ) -> dict[str, Any]:
        """Parse multiple characteristics at once."""

    @abstractmethod
    def parse_characteristic(
        self,
        uuid: str,
        raw_data: bytes,
        ctx: CharacteristicContext | None = None,
    ) -> Any:  # noqa: ANN401  # Runtime UUID dispatch cannot be type-safe
        """Parse a single characteristic's raw bytes."""

    @abstractmethod
    def get_characteristic_uuid_by_name(self, name: CharacteristicName) -> BluetoothUUID | None:
        """Get the UUID for a characteristic name enum (enum-only API)."""

    @abstractmethod
    def get_service_uuid_by_name(self, name: str | ServiceName) -> BluetoothUUID | None:
        """Get the UUID for a service name or enum."""

    def get_characteristic_info_by_name(self, name: CharacteristicName) -> Any | None:  # noqa: ANN401  # Adapter-specific characteristic info
        """Get characteristic info by enum name (optional method)."""
