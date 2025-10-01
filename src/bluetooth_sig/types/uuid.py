"""Bluetooth UUID utilities for handling 16-bit and 128-bit UUIDs."""

from __future__ import annotations

import re


class BluetoothUUID:
    """Bluetooth UUID class that handles both 16-bit and 128-bit UUIDs with automatic normalization and conversion.

    Supports various input formats:
    - Short form: "180F", "0x180F", "180f"
    - Full form: "0000180F-0000-1000-8000-00805F9B34FB"
    - Normalized: "0000180F00001000800000805F9B34FB"
    - Integer: 6159 (for 16-bit) or large integer (for 128-bit)

    Provides automatic conversion between formats and consistent comparison.
    """

    # Bluetooth SIG base UUID for 16-bit to 128-bit conversion
    BASE_UUID = "0000XXXX00001000800000805F9B34FB"

    # UUID validation constants
    INVALID_SHORT_UUID = "0000"
    INVALID_BASE_UUID_DASHED = "00000000-0000-1000-8000-00805f9b34fb"
    INVALID_BASE_UUID_NORMALIZED = "0000000000001000800000805F9B34FB"
    INVALID_NULL_UUID = "0000000000000000000000000000"
    INVALID_PLACEHOLDER_UUID = "0000123400001000800000805F9B34FB"

    UUID_SHORT_LEN = 4
    UUID_FULL_LEN = 32

    def __init__(self, uuid: str | int) -> None:
        """Initialize BluetoothUUID from a UUID string or integer.

        Args:
            uuid: UUID string in any valid format (short, full, dashed, hex-prefixed) or integer

        Raises:
            ValueError: If UUID format is invalid
        """
        if isinstance(uuid, int):
            self._normalized = self._normalize_uuid_from_int(uuid)
        else:
            self._normalized = self._normalize_uuid(uuid)

        # Validate the normalized form
        if not self._is_valid_normalized_uuid(self._normalized):
            raise ValueError(f"Invalid UUID format: {uuid}")

    @staticmethod
    def _normalize_uuid(uuid: str | BluetoothUUID) -> str:
        """Normalize UUID to uppercase hex without dashes or 0x prefix."""
        if isinstance(uuid, BluetoothUUID):
            return uuid._normalized

        cleaned = uuid.replace("-", "").replace(" ", "").upper()
        if cleaned.startswith("0X"):
            cleaned = cleaned[2:]

        # Validate it's hex
        if not re.match(r"^[0-9A-F]+$", cleaned):
            raise ValueError(f"Invalid UUID format: {uuid}")

        # Determine if it's 16-bit or 128-bit
        if len(cleaned) == BluetoothUUID.UUID_SHORT_LEN:
            # 16-bit UUID - expand to 128-bit
            return f"0000{cleaned}00001000800000805F9B34FB"
        elif len(cleaned) == BluetoothUUID.UUID_FULL_LEN:
            # Already 128-bit
            return cleaned
        else:
            raise ValueError(f"Invalid UUID length: {len(cleaned)} (expected 4 or 32 characters)")

    @staticmethod
    def _normalize_uuid_from_int(uuid_int: int) -> str:
        """Normalize UUID from integer to uppercase hex string."""
        if uuid_int < 0:
            raise ValueError(f"UUID integer cannot be negative: {uuid_int}")

        # Convert to hex and remove 0x prefix
        hex_str = hex(uuid_int)[2:].upper()

        # Pad to appropriate length
        if len(hex_str) <= BluetoothUUID.UUID_SHORT_LEN:
            # 16-bit UUID
            hex_str = hex_str.zfill(BluetoothUUID.UUID_SHORT_LEN)
        elif len(hex_str) <= BluetoothUUID.UUID_FULL_LEN:
            # 128-bit UUID
            hex_str = hex_str.zfill(BluetoothUUID.UUID_FULL_LEN)
        else:
            raise ValueError(f"UUID integer too large: {uuid_int}")

        return hex_str

    @staticmethod
    def _is_valid_normalized_uuid(normalized: str) -> bool:
        """Check if normalized UUID string is valid."""
        return len(normalized) in (BluetoothUUID.UUID_SHORT_LEN, BluetoothUUID.UUID_FULL_LEN) and bool(
            re.match(r"^[0-9A-F]+$", normalized)
        )

    @property
    def normalized(self) -> str:
        """Get normalized UUID (uppercase hex, no dashes, no 0x prefix)."""
        return self._normalized

    @property
    def is_short(self) -> bool:
        """Check if this is a 16-bit (short) UUID."""
        return len(self._normalized) == self.UUID_SHORT_LEN

    @property
    def is_full(self) -> bool:
        """Check if this is a 128-bit (full) UUID."""
        return len(self._normalized) == self.UUID_FULL_LEN

    @property
    def short_form(self) -> str:
        """Get 16-bit short form (e.g., '180F')."""
        if self.is_short:
            return self._normalized
        elif self.is_full:
            return self._normalized[4:8]
        else:
            raise ValueError(f"Invalid UUID length: {len(self._normalized)}")

    @property
    def full_form(self) -> str:
        """Get 128-bit full form with Bluetooth base UUID."""
        if self.is_full:
            return self._normalized
        elif self.is_short:
            return f"0000{self._normalized}00001000800000805F9B34FB"
        else:
            raise ValueError(f"Invalid UUID length: {len(self._normalized)}")

    @property
    def dashed_form(self) -> str:
        """Get UUID in standard dashed format (e.g., '0000180F-0000-1000-8000-00805F9B34FB')."""
        full = self.full_form
        return f"{full[:8]}-{full[8:12]}-{full[12:16]}-{full[16:20]}-{full[20:]}"

    @property
    def int_value(self) -> int:
        """Get UUID as integer value."""
        return int(self._normalized, 16)

    def matches(self, other: str | BluetoothUUID) -> bool:
        """Check if this UUID matches another UUID (handles format conversion automatically)."""
        if not isinstance(other, BluetoothUUID):
            other = BluetoothUUID(other)

        # Convert both to full form for comparison
        return self.full_form == other.full_form

    def __str__(self) -> str:
        """String representation - uses dashed form for readability."""
        return self.dashed_form

    def __repr__(self) -> str:
        """Representation showing the normalized form."""
        return f"BluetoothUUID('{self._normalized}')"

    def __eq__(self, other: object) -> bool:
        """Check equality with another UUID."""
        if not isinstance(other, (str, BluetoothUUID)):
            return NotImplemented
        return self.matches(other)

    def __hash__(self) -> int:
        """Hash based on normalized form."""
        return hash(self._normalized)

    def __lt__(self, other: str | BluetoothUUID) -> bool:
        """Less than comparison."""
        if not isinstance(other, BluetoothUUID):
            other = BluetoothUUID(other)
        return self._normalized < other._normalized

    def __le__(self, other: str | BluetoothUUID) -> bool:
        """Less than or equal comparison."""
        return self < other or self == other

    def __gt__(self, other: str | BluetoothUUID) -> bool:
        """Greater than comparison."""
        if not isinstance(other, BluetoothUUID):
            other = BluetoothUUID(other)
        return self._normalized > other._normalized

    def __ge__(self, other: str | BluetoothUUID) -> bool:
        """Greater than or equal comparison."""
        return self > other or self == other

    def __len__(self) -> int:
        """Return the length of the normalized UUID string."""
        return len(self._normalized)

    def is_valid_for_custom_characteristic(self) -> bool:
        """Check if this UUID is valid for custom characteristics.

        Returns:
            False if the UUID is any of the invalid/reserved UUIDs:
            - Base UUID (00000000-0000-1000-8000-00805f9b34fb)
            - Null UUID (all zeros)
            - Placeholder UUID (used internally)
            True otherwise
        """
        return self.normalized not in (
            self.INVALID_BASE_UUID_NORMALIZED,
            self.INVALID_NULL_UUID,
            self.INVALID_PLACEHOLDER_UUID,
        )
