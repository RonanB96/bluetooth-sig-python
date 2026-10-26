"""Resolvable Private Address Only characteristic (0x2AC9).

BT Core Spec v6.0, Vol 3, Part C, Section 12.5:
  Value shall be 1 octet in length (uint8).
  0 = only Resolvable Private Addresses will be used as local addresses
      after bonding.
  All other values are reserved for future use.
"""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class ResolvablePrivateAddressOnlyCharacteristic(BaseCharacteristic[int]):
    """Resolvable Private Address Only characteristic (0x2AC9).

    org.bluetooth.characteristic.resolvable_private_address_only

    A single uint8 indicating the device's RPA usage policy after bonding.
    Currently only value 0 is defined; all other values reserved.
    """

    expected_length: int = 1
    _template = Uint8Template()
