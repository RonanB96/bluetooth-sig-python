"""Protocol definitions for Bluetooth SIG standards."""

from __future__ import annotations

from typing import Any, Protocol

from .gatt_enums import GattProperty


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

    @property
    def properties(self) -> list[GattProperty]:
        """BLE GATT properties."""
        ...  # pylint: disable=unnecessary-ellipsis

    @property
    def name(self) -> str:
        """Characteristic name."""
        ...  # pylint: disable=unnecessary-ellipsis

    field_errors: list[Any]  # ParseFieldError, but avoid circular import
    parse_trace: list[str]


class CharacteristicProtocol(Protocol):
    """Protocol for characteristic validation and round-trip testing.

    Defines the minimal interface for characteristics that support
    parse/encode operations without requiring full BaseCharacteristic import.
    Used primarily by debug utilities.
    """

    def parse_value(self, data: bytearray) -> Any:  # noqa: ANN401
        """Parse raw data into characteristic value."""
        ...  # pylint: disable=unnecessary-ellipsis  # Ellipsis is required for Protocol method stubs

    def _encode_value(self, value: Any) -> bytearray:  # noqa: ANN401
        """Encode characteristic value into raw data."""
        ...  # pylint: disable=unnecessary-ellipsis  # Ellipsis is required for Protocol method stubs
