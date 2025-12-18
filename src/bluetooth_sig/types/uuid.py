"""Bluetooth UUID utilities for handling 16-bit and 128-bit UUIDs."""

from __future__ import annotations

import builtins
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

    # SIG base UUID suffix (everything after XXXX placeholder)
    SIG_BASE_SUFFIX = "00001000800000805F9B34FB"

    # Bluetooth SIG base UUID for 16-bit to 128-bit conversion
    BASE_UUID = f"0000XXXX{SIG_BASE_SUFFIX}"

    # UUID validation constants
    INVALID_SHORT_UUID = "0000"
    INVALID_BASE_UUID_DASHED = "00000000-0000-1000-8000-00805f9b34fb"
    INVALID_BASE_UUID_NORMALIZED = f"00000000{SIG_BASE_SUFFIX}"
    INVALID_NULL_UUID = "0000000000000000000000000000"
    INVALID_PLACEHOLDER_UUID = f"00001234{SIG_BASE_SUFFIX}"

    # SIG characteristic UUID ranges (from actual YAML data)
    SIG_CHARACTERISTIC_MIN = 0x2A00  # 10752
    SIG_CHARACTERISTIC_MAX = 0x2C24  # 11300

    # SIG service UUID ranges (from actual YAML data)
    SIG_SERVICE_MIN = 0x1800  # 6144
    SIG_SERVICE_MAX = 0x185C  # 6236

    UUID_SHORT_LEN = 4
    UUID_FULL_LEN = 32

    def __init__(self, uuid: str | int | BluetoothUUID) -> None:
        """Initialize BluetoothUUID from a UUID string or integer.

        Args:
            uuid: UUID string in any valid format (short, full, dashed, hex-prefixed) or integer

        Raises:
            ValueError: If UUID format is invalid

        """
        if isinstance(uuid, BluetoothUUID):
            return

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
            # Access to protected attribute is intentional for self-reference normalization
            return uuid._normalized  # pylint: disable=protected-access

        cleaned = uuid.replace("-", "").replace(" ", "").upper()
        if cleaned.startswith("0X"):
            cleaned = cleaned[2:]

        # Validate it's hex
        if not re.match(r"^[0-9A-F]+$", cleaned):
            raise ValueError(f"Invalid UUID format: {uuid}")

        # Determine if it's 16-bit or 128-bit
        if len(cleaned) == BluetoothUUID.UUID_SHORT_LEN:
            # 16-bit UUID - expand to 128-bit
            return f"0000{cleaned}{BluetoothUUID.SIG_BASE_SUFFIX}"
        if len(cleaned) == BluetoothUUID.UUID_FULL_LEN:
            # Already 128-bit
            return cleaned
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
        if self.is_full:
            return self._normalized[4:8]
        raise ValueError(f"Invalid UUID length: {len(self._normalized)}")

    @property
    def full_form(self) -> str:
        """Get 128-bit full form with Bluetooth base UUID."""
        if self.is_full:
            return self._normalized
        if self.is_short:
            return f"0000{self._normalized}{self.SIG_BASE_SUFFIX}"
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

    @property
    def bytes(self) -> builtins.bytes:
        """Get UUID as 16-byte binary representation (big-endian).

        Useful for BLE wire protocol operations where UUIDs need to be
        transmitted in binary format.

        Returns:
            16 bytes representing the full 128-bit UUID in big-endian byte order

        """
        # Always use full form (128-bit) for bytes representation
        full_int = int(self.full_form, 16)
        return full_int.to_bytes(16, byteorder="big")

    @property
    def bytes_le(self) -> builtins.bytes:
        """Get UUID as 16-byte binary representation (little-endian).

        Some BLE operations require little-endian byte order.

        Returns:
            16 bytes representing the full 128-bit UUID in little-endian byte order

        """
        # Always use full form (128-bit) for bytes representation
        full_int = int(self.full_form, 16)
        return full_int.to_bytes(16, byteorder="little")

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
        """Hash based on full form for consistency with __eq__."""
        return hash(self.full_form)

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

    def is_sig_characteristic(self) -> bool:
        """Check if this UUID is a Bluetooth SIG assigned characteristic UUID.

        Based on actual SIG assigned numbers from characteristic_uuids.yaml.
        Range verified: 0x2A00 to 0x2C24 (and potentially expanding).

        Returns:
            True if this is a SIG characteristic UUID, False otherwise

        """
        # Must be a full 128-bit UUID using SIG base UUID pattern
        if not self.is_full:
            return False

        # Check if it uses the SIG base UUID pattern by comparing with our constant
        if not self.normalized.endswith(self.SIG_BASE_SUFFIX):
            return False

        # Must start with "0000" to be a proper SIG UUID
        if not self.normalized.startswith("0000"):
            return False

        try:
            # Use existing short_form property instead of manual string slicing
            uuid_int = int(self.short_form, 16)

            # Check if it's in the SIG characteristic range using constants
            return self.SIG_CHARACTERISTIC_MIN <= uuid_int <= self.SIG_CHARACTERISTIC_MAX
        except ValueError:
            return False

    def is_sig_service(self) -> bool:
        """Check if this UUID is a Bluetooth SIG assigned service UUID.

        Based on actual SIG assigned numbers from service_uuids.yaml.
        Range verified: 0x1800 to 0x185C (and potentially expanding).

        Returns:
            True if this is a SIG service UUID, False otherwise

        """
        # Must be a full 128-bit UUID using SIG base UUID pattern
        if not self.is_full:
            return False

        # Check if it uses the SIG base UUID pattern by comparing with our constant
        if not self.normalized.endswith(self.SIG_BASE_SUFFIX):
            return False

        # Must start with "0000" to be a proper SIG UUID
        if not self.normalized.startswith("0000"):
            return False

        try:
            # Use existing short_form property instead of manual string slicing
            uuid_int = int(self.short_form, 16)

            # Check if it's in the SIG service range using constants
            return self.SIG_SERVICE_MIN <= uuid_int <= self.SIG_SERVICE_MAX
        except ValueError:
            return False
