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
    properties: list[GattProperty]
    name: str
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

    def encode_value(self, value: Any) -> bytearray:  # noqa: ANN401
        """Encode characteristic value into raw data."""
        ...  # pylint: disable=unnecessary-ellipsis  # Ellipsis is required for Protocol method stubs


# Import at the end to avoid circular import issues
try:
    import msgspec

    from .uuid import BluetoothUUID

    class ProtocolInfo(msgspec.Struct, frozen=True, kw_only=True):
        """Information about a Bluetooth protocol identifier.

        Attributes:
            uuid: The protocol's Bluetooth UUID
            name: Human-readable protocol name (e.g., "L2CAP", "RFCOMM")
        """

        uuid: BluetoothUUID
        name: str

        @property
        def protocol_type(self) -> str:
            """Extract protocol type from name.

            Returns the uppercase version of the protocol name for consistency.

            Returns:
                Protocol type as uppercase string (e.g., "L2CAP", "RFCOMM")
            """
            return self.name.upper()

except ImportError:
    # Fallback if msgspec or uuid not available (shouldn't happen in normal use)
    pass
