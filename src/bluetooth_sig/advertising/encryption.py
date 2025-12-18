"""Encryption key management for advertising data parsing.

This module provides protocols and implementations for managing
encryption keys used by encrypted BLE advertising protocols.

Includes support for:
- vendor-specific encryption (bindkeys for Xiaomi, BTHome, etc.)
- BLE-standard Encrypted Advertising Data (EAD) per Core Spec Supplement 1.23
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from bluetooth_sig.types.ead import EADKeyMaterial

if TYPE_CHECKING:
    from typing import TypeAlias

    AsyncKeyLookup: TypeAlias = Callable[[str], Awaitable[bytes | None]]

logger = logging.getLogger(__name__)


@runtime_checkable
class EADKeyProvider(Protocol):
    """Protocol for EAD encryption key lookup.

    Implement this protocol to provide EAD key material for devices
    that use BLE-standard Encrypted Advertising Data.

    Example:
        >>> class MyEADKeyProvider:
        ...     def __init__(self, keys: dict[str, EADKeyMaterial]):
        ...         self._keys = keys
        ...
        ...     def get_ead_key(self, mac_address: str) -> EADKeyMaterial | None:
        ...         return self._keys.get(mac_address.upper())
    """

    def get_ead_key(self, mac_address: str) -> EADKeyMaterial | None:
        """Get EAD key material for a device.

        Args:
            mac_address: Device MAC address (e.g., "AA:BB:CC:DD:EE:FF")

        Returns:
            EADKeyMaterial containing session key and IV,
            or None if no key is available for this device.
        """
        ...  # pylint: disable=unnecessary-ellipsis


@runtime_checkable
class EncryptionKeyProvider(Protocol):
    """Protocol for encryption key lookup.

    Implement this protocol to provide encryption keys for devices
    that use encrypted advertising (e.g., Xiaomi MiBeacon, BTHome).

    Example:
        >>> class MyKeyProvider:
        ...     def __init__(self, keys: dict[str, bytes]):
        ...         self._keys = keys
        ...
        ...     def get_key(self, mac_address: str) -> bytes | None:
        ...         return self._keys.get(mac_address.upper())

    """

    def get_key(self, mac_address: str) -> bytes | None:
        """Get encryption key for a device.

        Args:
            mac_address: Device MAC address (e.g., "AA:BB:CC:DD:EE:FF")

        Returns:
            Encryption key bytes (typically 16 bytes for AES-CCM),
            or None if no key is available for this device.

        """
        ...  # pylint: disable=unnecessary-ellipsis


class DictKeyProvider:
    """Simple dictionary-based encryption key provider.

    Stores keys in a dictionary mapping MAC addresses to key bytes.
    Supports both legacy bindkeys and EAD key material.
    Logs a warning once per unknown MAC address.

    Attributes:
        keys: Dictionary mapping MAC addresses to encryption keys
        ead_keys: Dictionary mapping MAC addresses to EAD key material
        warned_macs: Set of MAC addresses that have already been warned about

    Example:
        >>> provider = DictKeyProvider(
        ...     {
        ...         "AA:BB:CC:DD:EE:FF": bytes.fromhex("0123456789abcdef0123456789abcdef"),
        ...     }
        ... )
        >>> key = provider.get_key("AA:BB:CC:DD:EE:FF")
        >>> print(key.hex() if key else "No key")
        0123456789abcdef0123456789abcdef

    """

    def __init__(
        self,
        keys: dict[str, bytes] | None = None,
        ead_keys: dict[str, EADKeyMaterial] | None = None,
    ) -> None:
        """Initialize with optional key dictionaries.

        Args:
            keys: Dictionary mapping MAC addresses to encryption keys.
                  MAC addresses should be uppercase with colons.
            ead_keys: Dictionary mapping MAC addresses to EAD key material.

        """
        self.keys: dict[str, bytes] = {}
        self.ead_keys: dict[str, EADKeyMaterial] = {}
        self.warned_macs: set[str] = set()

        if keys:
            # Normalize MAC addresses to uppercase
            for mac, key in keys.items():
                self.keys[mac.upper()] = key

        if ead_keys:
            # Normalize MAC addresses to uppercase
            for mac, key_material in ead_keys.items():
                self.ead_keys[mac.upper()] = key_material

    def get_key(self, mac_address: str) -> bytes | None:
        """Get encryption key for a device.

        Args:
            mac_address: Device MAC address (e.g., "AA:BB:CC:DD:EE:FF")

        Returns:
            Encryption key bytes, or None if no key available.

        """
        normalized_mac = mac_address.upper()
        key = self.keys.get(normalized_mac)

        if key is None and normalized_mac not in self.warned_macs:
            # Mask MAC address in logs (show only last 4 chars) for privacy
            masked_mac = f"**:**:**:**:{normalized_mac[-5:]}"
            logger.debug("No encryption key for MAC %s", masked_mac)
            self.warned_macs.add(normalized_mac)

        return key

    def get_ead_key(self, mac_address: str) -> EADKeyMaterial | None:
        """Get EAD key material for a device.

        Args:
            mac_address: Device MAC address (e.g., "AA:BB:CC:DD:EE:FF")

        Returns:
            EADKeyMaterial containing session key and IV,
            or None if no key is available for this device.

        """
        normalized_mac = mac_address.upper()
        key_material = self.ead_keys.get(normalized_mac)

        if key_material is None and normalized_mac not in self.warned_macs:
            # Mask MAC address in logs (show only last 4 chars) for privacy
            masked_mac = f"**:**:**:**:{normalized_mac[-5:]}"
            logger.debug("No EAD key material for MAC %s", masked_mac)
            self.warned_macs.add(normalized_mac)

        return key_material

    def set_key(self, mac_address: str, key: bytes) -> None:
        """Set or update encryption key for a device.

        Args:
            mac_address: Device MAC address
            key: Encryption key bytes (typically 16 bytes)

        """
        normalized_mac = mac_address.upper()
        self.keys[normalized_mac] = key
        # Clear warning status if we now have a key
        self.warned_macs.discard(normalized_mac)

    def set_ead_key(self, mac_address: str, key_material: EADKeyMaterial) -> None:
        """Set or update EAD key material for a device.

        Args:
            mac_address: Device MAC address
            key_material: EAD key material (session key + IV)

        """
        normalized_mac = mac_address.upper()
        self.ead_keys[normalized_mac] = key_material
        # Clear warning status if we now have a key
        self.warned_macs.discard(normalized_mac)

    def remove_key(self, mac_address: str) -> None:
        """Remove encryption key for a device.

        Args:
            mac_address: Device MAC address

        """
        normalized_mac = mac_address.upper()
        self.keys.pop(normalized_mac, None)

    def remove_ead_key(self, mac_address: str) -> None:
        """Remove EAD key material for a device.

        Args:
            mac_address: Device MAC address

        """
        normalized_mac = mac_address.upper()
        self.ead_keys.pop(normalized_mac, None)


# AsyncKeyLookup type alias is defined in TYPE_CHECKING block at top of module
