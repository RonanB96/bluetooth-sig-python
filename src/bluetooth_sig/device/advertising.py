"""Advertising-related functionality for Device.

Manages advertising packet interpretation for a BLE device using
the composition pattern. This class is accessed via `device.advertising`.

Based on patterns from bleak (BLEDevice + BleakClient) and real-world
implementations (BTHome-BLE, Xiaomi-BLE).

Error Handling:
    Methods raise exceptions instead of returning status codes.
    This is consistent with GATT characteristic parsing and Pythonic patterns.

    Exceptions:
        EncryptionRequiredError: Payload encrypted, no bindkey available
        DecryptionFailedError: Decryption failed (wrong key or corrupt data)
        AdvertisingParseError: General parse failure (includes "no interpreter found")
"""

from __future__ import annotations

import logging
from typing import Callable, TypeVar, overload

from bluetooth_sig.advertising import AdvertisingPDUParser
from bluetooth_sig.advertising.base import AdvertisingData, PayloadInterpreter
from bluetooth_sig.advertising.exceptions import (
    AdvertisingParseError,
    DecryptionFailedError,
    EncryptionRequiredError,
)
from bluetooth_sig.advertising.registry import PayloadInterpreterRegistry
from bluetooth_sig.advertising.state import DeviceAdvertisingState
from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.types.advertising.result import AdvertisementData

logger = logging.getLogger(__name__)

# Type variable for generic interpreter return types
T = TypeVar("T")


class DeviceAdvertising:  # pylint: disable=too-many-instance-attributes
    """Manages advertising packet interpretation for a device.

    Accessed via `device.advertising`.

    Attributes:
        state: Current advertising state (caller-owned, mutable).
        mac_address: Device MAC address.

    Example:
        device = Device(mac_address="AA:BB:CC:DD:EE:FF", translator=translator)

        # Set bindkey for encrypted advertisements
        device.advertising.set_bindkey(bytes.fromhex("0102030405060708090a0b0c0d0e0f10"))

        # Subscribe to continuous advertisement updates
        def on_advertisement(ad_data: AdvertisementData, data: Any) -> None:
            if data is not None:
                print(f"Sensor data: {data}")

        device.advertising.subscribe(on_advertisement)

        # Later, unsubscribe
        device.advertising.unsubscribe(on_advertisement)

        # Or process single advertisement manually
        ad_data = AdvertisingData(
            manufacturer_data={},
            service_data={BluetoothUUID("0000fcd2-..."): payload},
            rssi=-60,
        )
        try:
            data = device.advertising.process(ad_data)
            print(f"Sensor data: {data}")
        except EncryptionRequiredError:
            print("Need bindkey")
        except AdvertisingParseError as e:
            print(f"Parse error: {e}")

    """

    def __init__(self, mac_address: str, connection_manager: ConnectionManagerProtocol) -> None:
        """Initialise advertising subsystem.

        Args:
            mac_address: Device MAC address.
            connection_manager: Connection manager for backend monitoring.

        """
        self._mac_address = mac_address
        self._connection_manager = connection_manager
        self.state = DeviceAdvertisingState(address=mac_address)
        self._interpreters: dict[str, PayloadInterpreter[object]] = {}
        self._registry: PayloadInterpreterRegistry | None = None
        self._pdu_parser = AdvertisingPDUParser()
        self._callbacks: list[Callable[[AdvertisementData, object], None]] = []
        self._backend_monitoring_enabled = False

    @property
    def mac_address(self) -> str:
        """Device MAC address."""
        return self._mac_address

    def set_registry(self, registry: PayloadInterpreterRegistry) -> None:
        """Set the interpreter registry for auto-detection.

        Args:
            registry: PayloadInterpreterRegistry to use for interpreter lookup.

        """
        self._registry = registry

    def register_interpreter(
        self,
        name: str,
        interpreter: PayloadInterpreter[object],
    ) -> None:
        """Register a named interpreter.

        Args:
            name: Unique name for the interpreter.
            interpreter: PayloadInterpreter instance.

        """
        self._interpreters[name] = interpreter

    def get_interpreter(self, name: str) -> PayloadInterpreter[object] | None:
        """Get an interpreter by name.

        Args:
            name: Interpreter name.

        Returns:
            PayloadInterpreter instance if found, None otherwise.

        """
        return self._interpreters.get(name)

    def set_bindkey(self, bindkey: bytes) -> None:
        """Set the encryption bindkey for decryption.

        Args:
            bindkey: 16-byte AES-CCM key.

        """
        self.state.encryption.bindkey = bindkey

    @overload
    def process(
        self,
        advertising_data: AdvertisingData,
        *,
        interpreter: type[PayloadInterpreter[T]],
    ) -> T: ...

    @overload
    def process(
        self,
        advertising_data: AdvertisingData,
    ) -> object: ...

    def process(
        self,
        advertising_data: AdvertisingData,
        *,
        interpreter: type[PayloadInterpreter[T]] | None = None,
    ) -> T | object:
        """Process an advertising payload.

        Type-safe path: Pass an interpreter class to get typed return.

        Args:
            advertising_data: Complete advertising data from BLE packet.
            interpreter: Interpreter class for type-safe parsing (recommended).

        Returns:
            Parsed data from the interpreter. Return type is inferred when
            passing interpreter class, otherwise returns object.

        Raises:
            AdvertisingParseError: No interpreter found or parse failure.
            EncryptionRequiredError: Payload encrypted, no bindkey available.
            DecryptionFailedError: Decryption failed (wrong key or corrupt data).

        Example:
            # Type-safe: IDE knows return type is BTHomeData
            data = device.advertising.process(ad_data, interpreter=BTHomeInterpreter)

            # Auto-detect: returns object
            data = device.advertising.process(ad_data)

        """
        # Type-safe path: use interpreter class directly
        if interpreter is not None:
            interp_instance = interpreter(self._mac_address)
            cached_name = interp_instance.info.name or interpreter.__name__
            # Cache for future auto-detection (variance: T is subtype of object)
            self._interpreters[cached_name] = interp_instance  # type: ignore[assignment]
            return self._run_interpreter(interp_instance, advertising_data)

        # Try registered interpreters first (returns object for dynamic dispatch)
        for registered_interp in self._interpreters.values():
            if registered_interp.supports(advertising_data):
                return registered_interp.interpret(advertising_data, self.state)

        # Try auto-detection via registry
        if self._registry is not None:
            detected_class = self._registry.find_interpreter_class(advertising_data)
            if detected_class is not None:
                # Create instance and cache it
                detected_instance = detected_class(self._mac_address)
                cached_name = detected_instance.info.name or detected_class.__name__
                self._interpreters[cached_name] = detected_instance
                result: object = detected_instance.interpret(advertising_data, self.state)
                return result

        raise AdvertisingParseError(message="No interpreter found for advertisement")

    def _run_interpreter(
        self,
        interpreter: PayloadInterpreter[T],
        advertising_data: AdvertisingData,
    ) -> T:
        """Run a single interpreter.

        Args:
            interpreter: The interpreter to run.
            advertising_data: Complete advertising data from BLE packet.

        Returns:
            Parsed data from the interpreter.

        Raises:
            EncryptionRequiredError: Payload encrypted, no bindkey available.
            DecryptionFailedError: Decryption failed.
            AdvertisingParseError: General parse failure.

        """
        # Interpreter raises exceptions on error, returns data on success
        return interpreter.interpret(advertising_data, self.state)

    @overload
    def process_from_connection_manager(
        self,
        advertisement: AdvertisementData,
        *,
        interpreter: type[PayloadInterpreter[T]],
    ) -> tuple[AdvertisementData, T]: ...

    @overload
    def process_from_connection_manager(
        self,
        advertisement: AdvertisementData,
    ) -> tuple[AdvertisementData, object | None]: ...

    def process_from_connection_manager(
        self,
        advertisement: AdvertisementData,
        *,
        interpreter: type[PayloadInterpreter[T]] | None = None,
    ) -> tuple[AdvertisementData, T] | tuple[AdvertisementData, object | None]:
        """Process advertisement from connection manager.

        Args:
            advertisement: AdvertisementData from connection manager
            interpreter: Interpreter class for type-safe parsing (optional).

        Returns:
            Tuple of (processed AdvertisementData, interpreted data or None)

        """
        # Convert AdvertisementData to BaseAdvertisingData for processing
        base_advertising_data = AdvertisingData(
            manufacturer_data=advertisement.ad_structures.core.manufacturer_data,
            service_data=advertisement.ad_structures.core.service_data,
            local_name=advertisement.ad_structures.core.local_name,
            rssi=advertisement.rssi or 0,
        )

        # Try to process, catching errors and returning None for data
        interpreted_data: T | object | None = None
        interpreter_name: str | None = None

        try:
            if interpreter is not None:
                interpreted_data = self.process(base_advertising_data, interpreter=interpreter)
                interpreter_name = interpreter.__name__
            else:
                interpreted_data = self.process(base_advertising_data)
                # Find which interpreter was used
                for name, interp in self._interpreters.items():
                    if interp.supports(base_advertising_data):
                        interpreter_name = name
                        break
        except (AdvertisingParseError, EncryptionRequiredError, DecryptionFailedError):
            # No data available on error
            pass

        # Create enriched AdvertisementData with interpretation
        processed_advertisement = AdvertisementData(
            ad_structures=advertisement.ad_structures,
            rssi=advertisement.rssi,
            interpreted_data=interpreted_data,
            interpreter_name=interpreter_name,
        )

        return processed_advertisement, interpreted_data

    @overload
    def parse_raw_pdu(
        self,
        raw_data: bytes,
        rssi: int = ...,
        *,
        interpreter: type[PayloadInterpreter[T]],
    ) -> tuple[AdvertisementData, T]: ...

    @overload
    def parse_raw_pdu(
        self,
        raw_data: bytes,
        rssi: int = ...,
    ) -> tuple[AdvertisementData, object | None]: ...

    def parse_raw_pdu(
        self,
        raw_data: bytes,
        rssi: int = 0,
        *,
        interpreter: type[PayloadInterpreter[T]] | None = None,
    ) -> tuple[AdvertisementData, T] | tuple[AdvertisementData, object | None]:
        """Parse raw advertising PDU bytes directly.

        Args:
            raw_data: Raw BLE advertising PDU bytes
            rssi: Received signal strength in dBm
            interpreter: Interpreter class for type-safe parsing (optional).

        Returns:
            Tuple of (parsed AdvertisementData, interpreted data or None)

        """
        # Parse raw PDU bytes
        pdu_result = self._pdu_parser.parse_advertising_data(raw_data)

        # Process through advertising subsystem (convert to BaseAdvertisingData)
        base_advertising_data = AdvertisingData(
            manufacturer_data=pdu_result.ad_structures.core.manufacturer_data,
            service_data=pdu_result.ad_structures.core.service_data,
            local_name=pdu_result.ad_structures.core.local_name,
            rssi=rssi,
        )

        # Try to process, catching errors and returning None for data
        interpreted_data: T | object | None = None
        interpreter_name: str | None = None

        try:
            if interpreter is not None:
                interpreted_data = self.process(base_advertising_data, interpreter=interpreter)
                interpreter_name = interpreter.__name__
            else:
                interpreted_data = self.process(base_advertising_data)
                # Find which interpreter was used
                for name, interp in self._interpreters.items():
                    if interp.supports(base_advertising_data):
                        interpreter_name = name
                        break
        except (AdvertisingParseError, EncryptionRequiredError, DecryptionFailedError):
            # No data available on error
            pass

        # Create AdvertisementData with interpretation
        advertisement = AdvertisementData(
            ad_structures=pdu_result.ad_structures,
            rssi=rssi,
            interpreted_data=interpreted_data,
            interpreter_name=interpreter_name,
        )

        return advertisement, interpreted_data

    def subscribe(
        self,
        callback: Callable[[AdvertisementData, object], None],
    ) -> None:
        """Subscribe to continuous advertisement updates.

        Registers a callback that will be invoked whenever new advertisements
        are received. Automatically enables backend monitoring when the first
        callback is registered.

        Args:
            callback: Function called with (AdvertisementData, interpreted_data)
                     when advertisements are received. interpreted_data is None
                     if parsing failed.
        """
        self._callbacks.append(callback)

        # Automatically enable backend monitoring for first subscriber
        if len(self._callbacks) == 1:
            self._enable_backend_monitoring()

    def unsubscribe(self, callback: Callable[[AdvertisementData, object], None] | None = None) -> None:
        """Unsubscribe from advertisement updates.

        If callback is provided, removes only that specific callback.
        If no callback is provided, removes all callbacks.
        Automatically disables backend monitoring when no callbacks remain.

        Args:
            callback: Specific callback to remove, or None to remove all

        """
        if callback is None:
            self._callbacks.clear()
        else:
            try:
                self._callbacks.remove(callback)
            except ValueError:
                logger.warning("Callback not found in subscriptions")

        # Automatically disable backend monitoring when no callbacks remain
        if not self._callbacks and self._backend_monitoring_enabled:
            self._disable_backend_monitoring()

    def _dispatch_to_callbacks(
        self,
        advertisement: AdvertisementData,
        interpreted_data: object,
    ) -> None:
        """Dispatch advertisement to all registered callbacks.

        Args:
            advertisement: Enriched AdvertisementData with interpreted_data
            interpreted_data: Parsed data from interpreter, or None if parsing failed

        """
        for callback in self._callbacks:
            try:
                callback(advertisement, interpreted_data)
            except Exception:  # pylint: disable=broad-exception-caught  # User callbacks may raise anything
                logger.exception("Advertisement callback raised exception")

    def _enable_backend_monitoring(self) -> None:
        """Enable backend monitoring (internal method)."""
        if self._backend_monitoring_enabled:
            return

        try:
            self._connection_manager.register_advertisement_callback(self._backend_callback_handler)
            self._backend_monitoring_enabled = True
        except NotImplementedError:
            backend_name = self._connection_manager.__class__.__name__
            logger.warning(
                "Backend %s does not support advertisement monitoring. "
                "Callbacks will not receive automatic updates. "
                "Use polling methods like refresh_advertisement() instead.",
                backend_name,
            )

    def _disable_backend_monitoring(self) -> None:
        """Disable backend monitoring (internal method)."""
        if self._backend_monitoring_enabled:
            self._connection_manager.unregister_advertisement_callback(self._backend_callback_handler)
            self._backend_monitoring_enabled = False

    def _backend_callback_handler(self, raw_advertisement: AdvertisementData) -> None:
        """Process raw advertisement and dispatch to subscribers."""
        try:
            processed_ad, interpreted_data = self.process_from_connection_manager(raw_advertisement)
            if self._callbacks:
                self._dispatch_to_callbacks(processed_ad, interpreted_data)
        except Exception:  # pylint: disable=broad-exception-caught  # Catch-all to prevent backend crashes
            logger.exception("Error processing backend advertisement")
