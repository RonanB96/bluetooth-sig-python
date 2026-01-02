"""Bluetooth address utilities.

This module provides utilities for working with Bluetooth device addresses
(BD_ADDR), commonly represented as 48-bit MAC addresses.
"""

from __future__ import annotations


def mac_address_to_bytes(mac_address: str) -> bytes:
    """Convert a MAC address string to 6 bytes.

    Args:
        mac_address: MAC address string (e.g., "AA:BB:CC:DD:EE:FF")

    Returns:
        6-byte representation of the MAC address

    Raises:
        ValueError: If MAC address format is invalid

    Example:
        >>> mac_address_to_bytes("AA:BB:CC:DD:EE:FF").hex()
        'aabbccddeeff'
    """
    # Remove colons/dashes and convert to bytes
    cleaned = mac_address.replace(":", "").replace("-", "")
    if len(cleaned) != 12:
        msg = f"Invalid MAC address format: {mac_address}"
        raise ValueError(msg)

    try:
        return bytes.fromhex(cleaned)
    except ValueError as err:
        msg = f"Invalid MAC address hex characters: {mac_address}"
        raise ValueError(msg) from err


def bytes_to_mac_address(data: bytes | bytearray) -> str:
    """Convert 6 bytes to a MAC address string.

    Args:
        data: 6-byte representation of MAC address

    Returns:
        MAC address string with colon separators (e.g., "AA:BB:CC:DD:EE:FF")

    Raises:
        ValueError: If data is not exactly 6 bytes

    Example:
        >>> bytes_to_mac_address(bytes.fromhex("aabbccddeeff"))
        'AA:BB:CC:DD:EE:FF'
    """
    if len(data) != 6:
        msg = f"MAC address must be exactly 6 bytes, got {len(data)}"
        raise ValueError(msg)
    return ":".join(f"{b:02X}" for b in data)


__all__ = ["mac_address_to_bytes", "bytes_to_mac_address"]
