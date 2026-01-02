"""BLE Advertising data parsing and interpretation framework.

Two-layer architecture:
- AdvertisingPDUParser: Low-level BLE PDU parsing (raw bytes → AD structures)
- AdvertisingDataInterpreter[T]: Base class for vendor-specific data interpretation
- EAD: Encrypted advertising data support (Core Spec 1.23)
"""

from __future__ import annotations

from bluetooth_sig.advertising.base import (
    AdvertisingDataInterpreter,
    AdvertisingInterpreterInfo,
    DataSource,
)
from bluetooth_sig.advertising.ead_decryptor import (
    EADDecryptor,
    build_ead_nonce,
    decrypt_ead,
    decrypt_ead_from_raw,
)
from bluetooth_sig.advertising.encryption import (
    DictKeyProvider,
    EADKeyProvider,
    EncryptionKeyProvider,
)
from bluetooth_sig.advertising.pdu_parser import AdvertisingPDUParser
from bluetooth_sig.advertising.registry import (
    AdvertisingInterpreterRegistry,
    advertising_interpreter_registry,
)
from bluetooth_sig.types.address import bytes_to_mac_address, mac_address_to_bytes

__all__ = [
    # PDU parser
    "AdvertisingPDUParser",
    # Interpreter base class
    "AdvertisingDataInterpreter",
    "AdvertisingInterpreterInfo",
    "DataSource",
    # Registry
    "AdvertisingInterpreterRegistry",
    "advertising_interpreter_registry",
    # Key providers
    "EncryptionKeyProvider",
    "DictKeyProvider",
    "EADKeyProvider",
    # EAD decryption
    "EADDecryptor",
    "decrypt_ead",
    "decrypt_ead_from_raw",
    "build_ead_nonce",
    # Address utilities
    "mac_address_to_bytes",
    "bytes_to_mac_address",
]
