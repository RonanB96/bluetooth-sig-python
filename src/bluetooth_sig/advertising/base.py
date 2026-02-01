"""Base classes for advertising data interpreters.

Advertising data interpretation follows a two-layer architecture:

1. PDU Parsing (AdvertisingPDUParser): Raw bytes → AD structures
   - Extracts manufacturer_data, service_data, flags, local_name, etc.
   - Framework-agnostic, works with raw BLE PDU bytes

2. Payload Interpretation (PayloadInterpreter): AD structures → typed results
   - Interprets vendor-specific protocols (BTHome, Xiaomi, RuuviTag, etc.)
   - Returns strongly-typed sensor data (temperature, humidity, etc.)
   - State managed externally by caller; interpreter updates state directly
   - Errors are raised as exceptions (consistent with GATT characteristic parsing)

Error Handling:
    Interpreters raise exceptions for error conditions instead of returning
    status codes. This is consistent with GATT characteristic parsing.

    Exceptions:
        EncryptionRequiredError: Payload encrypted, no bindkey available
        DecryptionFailedError: Decryption failed (wrong key or corrupt data)
        ReplayDetectedError: Counter not increasing (potential replay attack)
        DuplicatePacketError: Same packet_id as previous
        AdvertisingParseError: General parse failure
        UnsupportedVersionError: Unknown protocol version
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Generic, TypeVar

import msgspec

from bluetooth_sig.advertising.state import DeviceAdvertisingState
from bluetooth_sig.types.company import ManufacturerData
from bluetooth_sig.types.uuid import BluetoothUUID


class AdvertisingData(msgspec.Struct, kw_only=True, frozen=True):
    """Complete advertising data from a BLE advertisement packet.

    Encapsulates all extracted AD structures from a BLE PDU.
    Interpreters access only the fields they need.

    Attributes:
        manufacturer_data: Company ID → ManufacturerData mapping.
                          Each entry contains resolved company info and payload bytes.
        service_data: Service UUID → payload bytes mapping.
        local_name: Device local name (may contain protocol info).
        rssi: Signal strength in dBm.
        timestamp: Advertisement timestamp (Unix epoch seconds).

    """

    manufacturer_data: dict[int, ManufacturerData] = msgspec.field(default_factory=dict)
    service_data: dict[BluetoothUUID, bytes] = msgspec.field(default_factory=dict)
    local_name: str | None = None
    rssi: int | None = None
    timestamp: float | None = None


# Generic type variable for interpreter result types
T = TypeVar("T")


class DataSource(Enum):
    """Primary data source for interpreter routing."""

    MANUFACTURER = "manufacturer"
    SERVICE = "service"
    LOCAL_NAME = "local_name"


class InterpreterInfo(msgspec.Struct, kw_only=True, frozen=True):
    """Interpreter metadata for routing and identification.

    Attributes:
        company_id: Bluetooth SIG company ID for manufacturer data routing.
        service_uuid: Service UUID for service data routing.
        name: Human-readable interpreter name.
        data_source: Primary data source for fast routing.

    """

    company_id: int | None = None
    service_uuid: BluetoothUUID | None = None
    name: str = ""
    data_source: DataSource = DataSource.MANUFACTURER


class PayloadInterpreter(ABC, Generic[T]):
    """Base class for payload interpretation (service data + manufacturer data).

    Interprets raw bytes from BLE advertisements into typed domain objects.
    State is managed externally by the caller - interpreter receives state
    and updates it directly. Errors are raised as exceptions.

    Encryption Flow (following BTHome/Xiaomi patterns):
        1. Check if payload is encrypted (flag byte in payload header)
        2. If encrypted, check state.encryption.bindkey
        3. If no bindkey, raise EncryptionRequiredError
        4. Extract counter from payload, compare to state.encryption.encryption_counter
        5. If counter <= old counter, raise ReplayDetectedError
        6. Attempt decryption with AES-CCM
        7. If decryption fails, raise DecryptionFailedError
        8. Parse decrypted payload
        9. Update state.encryption.encryption_counter directly
        10. Return parsed data

    Example:
        class BTHomeInterpreter(PayloadInterpreter[BTHomeData]):
            _info = InterpreterInfo(
                service_uuid=BluetoothUUID("0000fcd2-0000-1000-8000-00805f9b34fb"),
                name="BTHome",
                data_source=DataSource.SERVICE,
            )

            @classmethod
            def supports(cls, advertising_data):
                return "0000fcd2-0000-1000-8000-00805f9b34fb" in advertising_data.service_data

            def interpret(self, advertising_data, state):
                # Parse BTHome service data
                # Update state.encryption.encryption_counter if encrypted
                # Raise exceptions on error
                # Return BTHomeData on success
                ...

    """

    _info: InterpreterInfo
    _is_base_class: bool = False

    def __init__(self, mac_address: str) -> None:
        """Create interpreter instance for a specific device.

        Args:
            mac_address: BLE device address (used for encryption nonce construction).

        """
        self._mac_address = mac_address

    @property
    def mac_address(self) -> str:
        """Device MAC address."""
        return self._mac_address

    @property
    def info(self) -> InterpreterInfo:
        """Interpreter metadata."""
        return self._info

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Auto-register interpreter subclasses with the registry."""
        super().__init_subclass__(**kwargs)

        if getattr(cls, "_is_base_class", False):
            return
        if not hasattr(cls, "_info"):
            return

        # Lazy import to avoid circular dependency at module load time
        from bluetooth_sig.advertising.registry import payload_interpreter_registry  # noqa: PLC0415

        payload_interpreter_registry.register(cls)

    @classmethod
    @abstractmethod
    def supports(cls, advertising_data: AdvertisingData) -> bool:
        """Check if this interpreter handles the advertisement.

        Called by registry for fast routing. Should be a quick check
        based on company_id, service_uuid, or local_name pattern.

        Args:
            advertising_data: Complete advertising data from BLE packet.

        Returns:
            True if this interpreter can handle the advertisement.

        """

    @abstractmethod
    def interpret(
        self,
        advertising_data: AdvertisingData,
        state: DeviceAdvertisingState,
    ) -> T:
        """Interpret payload bytes and return typed result.

        Updates state directly (state is mutable). Raises exceptions for errors.

        Args:
            advertising_data: Complete advertising data from BLE packet.
            state: Current device advertising state (caller-managed, mutable).

        Returns:
            Parsed data of type T.

        Raises:
            EncryptionRequiredError: Payload encrypted, no bindkey available.
            DecryptionFailedError: Decryption failed.
            ReplayDetectedError: Encryption counter not increasing.
            DuplicatePacketError: Same packet_id as previous.
            AdvertisingParseError: General parse failure.
            UnsupportedVersionError: Unknown protocol version.

        """
