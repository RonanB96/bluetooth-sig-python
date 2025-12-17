"""BLE Advertising data parsing and interpretation framework.

Two-layer architecture:
- AdvertisingPDUParser: Low-level BLE PDU parsing (raw bytes → AD structures)
- AdvertisingDataInterpreter[T]: Base class for vendor-specific data interpretation
- EAD: Encrypted advertising data support (Core Spec 1.23)
"""

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
    mac_address_to_bytes,
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
    "mac_address_to_bytes",
]
