"""BLE Advertising data parsing and interpretation framework.

Two-layer architecture:
- AdvertisingPDUParser: Low-level BLE PDU parsing (raw bytes → AD structures)
- PayloadInterpreter[T]: Base class for payload interpretation (service data + manufacturer data)
- AdvertisingServiceResolver: Map service UUIDs → GATT service classes
- SIGCharacteristicInterpreter: Built-in interpreter for SIG characteristic service data
- EAD: Encrypted advertising data support (Core Spec 1.23)

State Management:
    Interpreters do NOT manage state. The caller (connection manager, device tracker)
    owns the DeviceAdvertisingState and passes it to interpreters.
    Interpreters receive state and return InterpretationResult with any updates.
"""

from __future__ import annotations

from bluetooth_sig.advertising.base import (
    AdvertisingData,
    DataSource,
    InterpreterInfo,
    PayloadInterpreter,
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
    PayloadContext,
    PayloadInterpreterRegistry,
    parse_advertising_payloads,
    payload_interpreter_registry,
)
from bluetooth_sig.advertising.result import InterpretationResult, InterpretationStatus
from bluetooth_sig.advertising.service_data_parser import ServiceDataParser
from bluetooth_sig.advertising.service_resolver import (
    AdvertisingServiceResolver,
    ResolvedService,
)
from bluetooth_sig.advertising.sig_characteristic_interpreter import (
    SIGCharacteristicData,
    SIGCharacteristicInterpreter,
)
from bluetooth_sig.advertising.state import (
    DeviceAdvertisingState,
    EncryptionState,
    PacketState,
)
from bluetooth_sig.types.address import bytes_to_mac_address, mac_address_to_bytes
from bluetooth_sig.types.company import CompanyIdentifier, ManufacturerData

__all__ = [
    "AdvertisingData",
    "AdvertisingPDUParser",
    "AdvertisingServiceResolver",
    "CompanyIdentifier",
    "DataSource",
    "DeviceAdvertisingState",
    "DictKeyProvider",
    "EADDecryptor",
    "EADKeyProvider",
    "EncryptionKeyProvider",
    "EncryptionState",
    "InterpretationResult",
    "InterpretationStatus",
    "InterpreterInfo",
    "ManufacturerData",
    "PacketState",
    "PayloadContext",
    "PayloadInterpreter",
    "PayloadInterpreterRegistry",
    "ResolvedService",
    "SIGCharacteristicData",
    "SIGCharacteristicInterpreter",
    "ServiceDataParser",
    "build_ead_nonce",
    "bytes_to_mac_address",
    "decrypt_ead",
    "decrypt_ead_from_raw",
    "mac_address_to_bytes",
    "parse_advertising_payloads",
    "payload_interpreter_registry",
]
