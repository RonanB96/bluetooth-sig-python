"""Unknown characteristic implementation for non-SIG characteristics."""

from __future__ import annotations

from typing import Any

from ...types import CharacteristicInfo
from ...types.gatt_enums import GattProperty
from ..context import CharacteristicContext
from .base import BaseCharacteristic


class UnknownCharacteristic(BaseCharacteristic[bytes]):
    """Generic characteristic implementation for unknown/non-SIG characteristics.

    This class provides basic functionality for characteristics that are not
    defined in the Bluetooth SIG specification. It stores raw data without
    attempting to parse it into structured types.
    """

    # NOTE: Exempt from registry validation — UnknownCharacteristic has no fixed UUID
    _is_base_class = True

    def __init__(
        self,
        info: CharacteristicInfo,
        properties: list[GattProperty] | None = None,
    ) -> None:
        """Initialize an unknown characteristic.

        Args:
            info: CharacteristicInfo object with UUID, name, unit, python_type
            properties: Runtime BLE properties discovered from device (optional)

        Raises:
            ValueError: If UUID is invalid

        """
        # If no name provided, generate one from UUID
        if not info.name:
            info = CharacteristicInfo(
                uuid=info.uuid,
                name=f"Unknown Characteristic ({info.uuid})",
                unit=info.unit or "",
                python_type=info.python_type,
            )

        super().__init__(info=info, properties=properties)

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bytes:  # Context type varies
        """Return raw bytes for unknown characteristics.

        Args:
            data: Raw bytes from the characteristic read
            ctx: Optional context (ignored)
            validate: Whether to validate ranges (default True)

        Returns:
            Raw bytes as-is

        """
        return bytes(data)

    def _encode_value(self, data: Any) -> bytearray:  # noqa: ANN401  # Accepts bytes-like objects
        """Encode data to bytes for unknown characteristics.

        Args:
            data: Data to encode (must be bytes or bytearray)

        Returns:
            Encoded bytes

        Raises:
            ValueError: If data is not bytes/bytearray

        """
        if isinstance(data, (bytes, bytearray)):
            return bytearray(data)
        raise ValueError(f"Unknown characteristics require bytes data, got {type(data)}")
