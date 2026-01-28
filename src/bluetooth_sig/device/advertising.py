"""Advertising-related functionality for Device.

Manages advertising packet interpretation for a BLE device using
the composition pattern. This class is accessed via `device.advertising`.

Based on patterns from bleak (BLEDevice + BleakClient) and real-world
implementations (BTHome-BLE, Xiaomi-BLE).
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from bluetooth_sig.advertising import AdvertisingPDUParser
from bluetooth_sig.advertising.base import AdvertisingData, PayloadInterpreter
from bluetooth_sig.advertising.registry import PayloadInterpreterRegistry
from bluetooth_sig.advertising.result import InterpretationResult, InterpretationStatus
from bluetooth_sig.advertising.state import DeviceAdvertisingState
from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.types import AdvertisementData

logger = logging.getLogger(__name__)


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
        def on_advertisement(ad_data: AdvertisementData, result: InterpretationResult) -> None:
            if result.is_success:
                print(f"Sensor data: {result.data}")

        device.advertising.subscribe(on_advertisement)

        # Later, unsubscribe
        device.advertising.unsubscribe(on_advertisement)

        # Or process single advertisement manually
        ad_data = AdvertisingData(
            manufacturer_data={},
            service_data={BluetoothUUID("0000fcd2-..."): payload},
            rssi=-60,
        )
        result = device.advertising.process(ad_data)

        if result.is_success:
            print(f"Sensor data: {result.data}")

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
        self._interpreters: dict[str, PayloadInterpreter[Any]] = {}
        self._registry: PayloadInterpreterRegistry | None = None
        self._pdu_parser = AdvertisingPDUParser()
        self._callbacks: list[Callable[[AdvertisementData, InterpretationResult[Any]], None]] = []
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
        interpreter: PayloadInterpreter[Any],
    ) -> None:
        """Register a named interpreter.

        Args:
            name: Unique name for the interpreter.
            interpreter: PayloadInterpreter instance.

        """
        self._interpreters[name] = interpreter

    def get_interpreter(self, name: str) -> PayloadInterpreter[Any] | None:
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

    def process(
        self,
        advertising_data: AdvertisingData,
        *,
        interpreter_name: str | None = None,
    ) -> InterpretationResult[Any]:
        """Process an advertising payload.

        If interpreter_name is provided, uses that specific interpreter.
        Otherwise, attempts auto-detection via registered interpreters
        or the registry.

        Args:
            advertising_data: Complete advertising data from BLE packet.
            interpreter_name: Specific interpreter to use (optional).

        Returns:
            InterpretationResult with parsed data and status.

        """
        # Use specific interpreter if requested
        if interpreter_name is not None:
            interpreter = self._interpreters.get(interpreter_name)
            if interpreter is None:
                return InterpretationResult(
                    status=InterpretationStatus.PARSE_ERROR,
                    error_message=f"Interpreter '{interpreter_name}' not registered",
                )
            return self._run_interpreter(interpreter, advertising_data)

        # Try registered interpreters first
        for interpreter in self._interpreters.values():
            if interpreter.supports(advertising_data):
                return self._run_interpreter(interpreter, advertising_data)

        # Try auto-detection via registry
        if self._registry is not None:
            interpreter_class = self._registry.find_interpreter_class(advertising_data)
            if interpreter_class is not None:
                # Create instance and cache it
                interpreter = interpreter_class(self._mac_address)
                interpreter_name = interpreter.info.name or interpreter_class.__name__
                self._interpreters[interpreter_name] = interpreter
                return self._run_interpreter(interpreter, advertising_data)

        return InterpretationResult(
            status=InterpretationStatus.PARSE_ERROR,
            error_message="No interpreter found for advertisement",
        )

    def _run_interpreter(
        self,
        interpreter: PayloadInterpreter[Any],
        advertising_data: AdvertisingData,
    ) -> InterpretationResult[Any]:
        """Run a single interpreter and apply state updates.

        Args:
            interpreter: The interpreter to run.
            advertising_data: Complete advertising data from BLE packet.

        Returns:
            InterpretationResult from the interpreter.

        """
        result = interpreter.interpret(advertising_data, self.state)

        # Apply state updates if successful
        if result.is_success:
            result.apply_to_state(self.state)

        return result

    def process_from_connection_manager(
        self,
        advertisement: AdvertisementData,
    ) -> tuple[AdvertisementData, Any]:
        """Process advertisement from connection manager.

        Args:
            advertisement: AdvertisementData from connection manager

        Returns:
            Tuple of (processed AdvertisementData, interpretation result)

        """
        # Convert AdvertisementData to BaseAdvertisingData for processing
        base_advertising_data = AdvertisingData(
            manufacturer_data=advertisement.ad_structures.core.manufacturer_data,
            service_data=advertisement.ad_structures.core.service_data,
            local_name=advertisement.ad_structures.core.local_name,
            rssi=advertisement.rssi or 0,
        )
        result = self.process(base_advertising_data)

        # Determine interpreter name from last successful interpretation
        interpreter_name: str | None = None
        if result.is_success:
            # Try to find which interpreter was used
            for name, interp in self._interpreters.items():
                if interp.supports(base_advertising_data):
                    interpreter_name = name
                    break

        # Create enriched AdvertisementData with interpretation
        processed_advertisement = AdvertisementData(
            ad_structures=advertisement.ad_structures,
            rssi=advertisement.rssi,
            interpreted_data=result.data if result.is_success else None,
            interpreter_name=interpreter_name,
        )

        return processed_advertisement, result

    def parse_raw_pdu(
        self,
        raw_data: bytes,
        rssi: int = 0,
    ) -> tuple[AdvertisementData, Any]:
        """Parse raw advertising PDU bytes directly.

        Args:
            raw_data: Raw BLE advertising PDU bytes
            rssi: Received signal strength in dBm

        Returns:
            Tuple of (parsed AdvertisementData, interpretation result)

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
        result = self.process(base_advertising_data)

        # Determine interpreter name from last successful interpretation
        interpreter_name: str | None = None
        if result.is_success:
            # Try to find which interpreter was used
            for name, interp in self._interpreters.items():
                if interp.supports(base_advertising_data):
                    interpreter_name = name
                    break

        # Create AdvertisementData with interpretation
        advertisement = AdvertisementData(
            ad_structures=pdu_result.ad_structures,
            rssi=rssi,
            interpreted_data=result.data if result.is_success else None,
            interpreter_name=interpreter_name,
        )

        return advertisement, result

    def subscribe(
        self,
        callback: Callable[[AdvertisementData, InterpretationResult[Any]], None],
    ) -> None:
        """Subscribe to continuous advertisement updates.

        Registers a callback that will be invoked whenever new advertisements
        are received. Automatically enables backend monitoring when the first
        callback is registered.

        Args:
            callback: Function called with (AdvertisementData, InterpretationResult)
                     when advertisements are received.
        """
        self._callbacks.append(callback)

        # Automatically enable backend monitoring for first subscriber
        if len(self._callbacks) == 1:
            self._enable_backend_monitoring()

    def unsubscribe(
        self, callback: Callable[[AdvertisementData, InterpretationResult[Any]], None] | None = None
    ) -> None:
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
        result: InterpretationResult[Any],
    ) -> None:
        """Dispatch advertisement to all registered callbacks.

        Args:
            advertisement: Enriched AdvertisementData with interpreted_data
            result: InterpretationResult from processing

        """
        for callback in self._callbacks:
            try:
                callback(advertisement, result)
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
            processed_ad, result = self.process_from_connection_manager(raw_advertisement)
            if self._callbacks:
                self._dispatch_to_callbacks(processed_ad, result)
        except Exception:  # pylint: disable=broad-exception-caught  # Catch-all to prevent backend crashes
            logger.exception("Error processing backend advertisement")
