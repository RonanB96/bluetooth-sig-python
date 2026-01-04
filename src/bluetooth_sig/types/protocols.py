"""Protocol definitions for Bluetooth SIG standards."""

from __future__ import annotations

from typing import Any, Protocol


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
