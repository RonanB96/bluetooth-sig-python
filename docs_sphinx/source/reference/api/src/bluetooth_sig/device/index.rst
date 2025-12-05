src.bluetooth_sig.device
========================

.. py:module:: src.bluetooth_sig.device

.. autoapi-nested-parse::

   Device class for grouping BLE device services, characteristics, encryption, and advertiser data.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /reference/api/src/bluetooth_sig/device/advertising_parser/index
   /reference/api/src/bluetooth_sig/device/connection/index
   /reference/api/src/bluetooth_sig/device/device/index


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.device.Device
   src.bluetooth_sig.device.SIGTranslatorProtocol


Package Contents
----------------

.. py:class:: Device(address: str, translator: SIGTranslatorProtocol)

   High-level BLE device abstraction.

   This class groups all services, characteristics, encryption requirements, and
   advertiser data for a BLE device. It integrates with
   [BluetoothSIGTranslator][bluetooth_sig.BluetoothSIGTranslator]
   for parsing while providing a unified view of device state.

   Key features:
   - Parse advertiser data from BLE scan results
   - Discover GATT services and characteristics via connection manager
   - Access parsed characteristic data by UUID
   - Handle device encryption requirements
   - Cache device information for performance

   .. admonition:: Example

      Create and configure a device:
      
      ```python
      from bluetooth_sig import BluetoothSIGTranslator
      from bluetooth_sig.device import Device
      
      translator = BluetoothSIGTranslator()
      device = Device("AA:BB:CC:DD:EE:FF", translator)
      
      # Attach connection manager and discover services
      device.attach_connection_manager(manager)
      await device.connect()
      await device.discover_services()
      
      # Read characteristic
      battery = await device.read("battery_level")
      print(f"Battery: {battery.value}%")
      ```


   .. py:attribute:: address


   .. py:attribute:: translator


   .. py:attribute:: connection_manager
      :type:  src.bluetooth_sig.device.connection.ConnectionManagerProtocol | None
      :value: None



   .. py:attribute:: services
      :type:  dict[str, src.bluetooth_sig.types.device_types.DeviceService]


   .. py:attribute:: encryption


   .. py:attribute:: advertiser_data


   .. py:attribute:: advertising_parser


   .. py:method:: attach_connection_manager(manager: src.bluetooth_sig.device.connection.ConnectionManagerProtocol) -> None

      Attach a connection manager to handle BLE connections.

      :param manager: Connection manager implementing the ConnectionManagerProtocol



   .. py:method:: detach_connection_manager() -> None
      :async:


      Detach the current connection manager and disconnect if connected.

      Disconnects if a connection manager is present, then removes it.



   .. py:method:: scan(manager_class: type[src.bluetooth_sig.device.connection.ConnectionManagerProtocol], timeout: float = 5.0) -> list[src.bluetooth_sig.types.device_types.ScannedDevice]
      :staticmethod:

      :async:


      Scan for nearby BLE devices using a specific connection manager.

      This is a static method that doesn't require a Device instance.
      Use it to discover devices before creating Device instances.

      :param manager_class: The connection manager class to use for scanning
                            (e.g., BleakRetryConnectionManager)
      :param timeout: Scan duration in seconds (default: 5.0)

      :returns: List of discovered devices

      :raises NotImplementedError: If the connection manager doesn't support scanning

      .. admonition:: Example

         ```python
         from bluetooth_sig.device import Device
         from connection_managers.bleak_retry import BleakRetryConnectionManager
         
         # Scan for devices
         devices = await Device.scan(BleakRetryConnectionManager, timeout=10.0)
         
         # Create Device instance for first discovered device
         if devices:
             translator = BluetoothSIGTranslator()
             device = Device(devices[0].address, translator)
         ```



   .. py:method:: connect() -> None
      :async:


      Connect to the BLE device.

      :raises RuntimeError: If no connection manager is attached



   .. py:method:: disconnect() -> None
      :async:


      Disconnect from the BLE device.

      :raises RuntimeError: If no connection manager is attached



   .. py:method:: read(char_name: str | src.bluetooth_sig.gatt.characteristics.CharacteristicName, resolution_mode: DependencyResolutionMode = DependencyResolutionMode.NORMAL) -> Any | None
      :async:


      Read a characteristic value from the device.

      :param char_name: Name or enum of the characteristic to read
      :param resolution_mode: How to handle automatic dependency resolution:
                              - NORMAL: Auto-resolve dependencies, use cache when available (default)
                              - SKIP_DEPENDENCIES: Skip dependency resolution and validation
                              - FORCE_REFRESH: Re-read dependencies from device, ignoring cache

      :returns: Parsed characteristic value or None if read fails

      :raises RuntimeError: If no connection manager is attached
      :raises ValueError: If required dependencies cannot be resolved

      .. admonition:: Example

         ```python
         # Read RSC Measurement - automatically reads/caches RSC Feature first
         measurement = await device.read(CharacteristicName.RSC_MEASUREMENT)
         
         # Read again - uses cached RSC Feature, no redundant BLE read
         measurement2 = await device.read(CharacteristicName.RSC_MEASUREMENT)
         
         # Force fresh read of feature characteristic
         measurement3 = await device.read(
             CharacteristicName.RSC_MEASUREMENT, resolution_mode=DependencyResolutionMode.FORCE_REFRESH
         )
         ```



   .. py:method:: write(char_name: str | src.bluetooth_sig.gatt.characteristics.CharacteristicName, data: bytes, response: bool = True) -> None
      :async:


      Write data to a characteristic on the device.

      :param char_name: Name or enum of the characteristic to write to
      :param data: Raw bytes to write
      :param response: If True, use write-with-response (wait for acknowledgment).
                       If False, use write-without-response (faster but no confirmation).
                       Default is True for reliability.

      :raises RuntimeError: If no connection manager is attached



   .. py:method:: start_notify(char_name: str | src.bluetooth_sig.gatt.characteristics.CharacteristicName, callback: Callable[[Any], None]) -> None
      :async:


      Start notifications for a characteristic.

      :param char_name: Name or enum of the characteristic to monitor
      :param callback: Function to call when notifications are received

      :raises RuntimeError: If no connection manager is attached



   .. py:method:: stop_notify(char_name: str | src.bluetooth_sig.gatt.characteristics.CharacteristicName) -> None
      :async:


      Stop notifications for a characteristic.

      :param char_name: Characteristic name or UUID



   .. py:method:: read_descriptor(desc_uuid: src.bluetooth_sig.types.uuid.BluetoothUUID | src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor) -> src.bluetooth_sig.types.DescriptorData
      :async:


      Read a descriptor value from the device.

      :param desc_uuid: UUID of the descriptor to read or BaseDescriptor instance

      :returns: Parsed descriptor data with metadata

      :raises RuntimeError: If no connection manager is attached



   .. py:method:: write_descriptor(desc_uuid: src.bluetooth_sig.types.uuid.BluetoothUUID | src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor, data: bytes | src.bluetooth_sig.types.DescriptorData) -> None
      :async:


      Write data to a descriptor on the device.

      :param desc_uuid: UUID of the descriptor to write to or BaseDescriptor instance
      :param data: Either raw bytes to write, or a DescriptorData object.
                   If DescriptorData is provided, its raw_data will be written.

      :raises RuntimeError: If no connection manager is attached



   .. py:method:: pair() -> None
      :async:


      Pair with the device.

      Raises an exception if pairing fails.

      :raises RuntimeError: If no connection manager is attached



   .. py:method:: unpair() -> None
      :async:


      Unpair from the device.

      Raises an exception if unpairing fails.

      :raises RuntimeError: If no connection manager is attached



   .. py:method:: read_rssi() -> int
      :async:


      Read the RSSI (signal strength) of the connection.

      :returns: RSSI value in dBm (typically negative, e.g., -60)

      :raises RuntimeError: If no connection manager is attached



   .. py:method:: set_disconnected_callback(callback: Callable[[], None]) -> None

      Set a callback to be invoked when the device disconnects.

      :param callback: Function to call when disconnection occurs

      :raises RuntimeError: If no connection manager is attached



   .. py:property:: mtu_size
      :type: int


      Get the negotiated MTU size in bytes.

      :returns: The MTU size negotiated for this connection (typically 23-512 bytes)

      :raises RuntimeError: If no connection manager is attached


   .. py:method:: parse_advertiser_data(raw_data: bytes) -> None

      Parse raw advertising data and update device information.

      :param raw_data: Raw bytes from BLE advertising packet



   .. py:method:: get_characteristic_data(char_uuid: src.bluetooth_sig.types.uuid.BluetoothUUID) -> src.bluetooth_sig.gatt.characteristics.base.CharacteristicData | None

      Get parsed characteristic data - single source of truth via characteristic.last_parsed.

      Searches across all services to find the characteristic by UUID.

      :param char_uuid: UUID of the characteristic

      :returns: CharacteristicData (last parsed result) if found, None otherwise.

      .. admonition:: Example

         ```python
         # Search for characteristic across all services
         battery_data = device.get_characteristic_data(BluetoothUUID("2A19"))
         if battery_data:
             print(f"Battery: {battery_data.value}%")
         ```



   .. py:method:: discover_services() -> dict[str, Any]
      :async:


      Discover services and characteristics from the connected BLE device.

      This method performs BLE service discovery using the attached connection
      manager, retrieving the device's service structure with characteristics
      and their runtime properties (READ, WRITE, NOTIFY, etc.).

      The discovered services are stored in `self.services` as DeviceService
      objects with properly instantiated characteristic classes from the registry.

      This implements the standard BLE workflow:
          1. await device.connect()
          2. await device.discover_services()  # This method
          3. value = await device.read("battery_level")

      .. note::

         - This method discovers the SERVICE STRUCTURE (what services/characteristics
           exist and their properties), but does NOT read characteristic VALUES.
         - Use `read()` to retrieve actual characteristic values after discovery.
         - Services are cached in `self.services` keyed by service UUID string.

      :returns: Dictionary mapping service UUIDs to DeviceService objects

      :raises RuntimeError: If no connection manager is attached

      .. admonition:: Example

         ```python
         device = Device(address, translator)
         device.attach_connection_manager(manager)
         
         await device.connect()
         services = await device.discover_services()  # Discover structure
         
         # Now services are available
         for service_uuid, device_service in services.items():
             print(f"Service: {service_uuid}")
             for char_uuid, char_instance in device_service.characteristics.items():
                 print(f"  Characteristic: {char_uuid}")
         
         # Read characteristic values
         battery = await device.read("battery_level")
         ```



   .. py:method:: get_characteristic_info(char_uuid: str) -> Any | None
      :async:


      Get information about a characteristic from the connection manager.

      :param char_uuid: UUID of the characteristic

      :returns: Characteristic information or None if not found

      :raises RuntimeError: If no connection manager is attached



   .. py:method:: read_multiple(char_names: list[str | src.bluetooth_sig.gatt.characteristics.CharacteristicName]) -> dict[str, Any | None]
      :async:


      Read multiple characteristics in batch.

      :param char_names: List of characteristic names or enums to read

      :returns: Dictionary mapping characteristic UUIDs to parsed values

      :raises RuntimeError: If no connection manager is attached



   .. py:method:: write_multiple(data_map: dict[str | src.bluetooth_sig.gatt.characteristics.CharacteristicName, bytes], response: bool = True) -> dict[str, bool]
      :async:


      Write to multiple characteristics in batch.

      :param data_map: Dictionary mapping characteristic names/enums to data bytes
      :param response: If True, use write-with-response for all writes.
                       If False, use write-without-response for all writes.

      :returns: Dictionary mapping characteristic UUIDs to success status

      :raises RuntimeError: If no connection manager is attached



   .. py:property:: device_info
      :type: src.bluetooth_sig.gatt.context.DeviceInfo


      Get cached device info object.

      :returns: DeviceInfo with current device metadata


   .. py:property:: name
      :type: str


      Get the device name.


   .. py:property:: is_connected
      :type: bool


      Check if the device is currently connected.

      :returns: True if connected, False otherwise


   .. py:method:: get_service_by_uuid(service_uuid: str) -> src.bluetooth_sig.types.device_types.DeviceService | None

      Get a service by its UUID.

      :param service_uuid: UUID of the service

      :returns: DeviceService instance or None if not found



   .. py:method:: get_services_by_name(service_name: str | src.bluetooth_sig.gatt.services.ServiceName) -> list[src.bluetooth_sig.types.device_types.DeviceService]

      Get services by name.

      :param service_name: Name or enum of the service

      :returns: List of matching DeviceService instances



   .. py:method:: list_characteristics(service_uuid: str | None = None) -> dict[str, list[str]]

      List all characteristics, optionally filtered by service.

      :param service_uuid: Optional service UUID to filter by

      :returns: Dictionary mapping service UUIDs to lists of characteristic UUIDs



.. py:class:: SIGTranslatorProtocol

   Bases: :py:obj:`Protocol`


   Protocol for SIG translator interface.


   .. py:method:: parse_characteristics(char_data: dict[str, bytes], ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> dict[str, src.bluetooth_sig.gatt.characteristics.base.CharacteristicData]
      :abstractmethod:


      Parse multiple characteristics at once.



   .. py:method:: parse_characteristic(uuid: str, raw_data: bytes, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> src.bluetooth_sig.gatt.characteristics.base.CharacteristicData
      :abstractmethod:


      Parse a single characteristic's raw bytes.



   .. py:method:: get_characteristic_uuid_by_name(name: src.bluetooth_sig.gatt.characteristics.CharacteristicName) -> src.bluetooth_sig.types.uuid.BluetoothUUID | None
      :abstractmethod:


      Get the UUID for a characteristic name enum (enum-only API).



   .. py:method:: get_service_uuid_by_name(name: str | src.bluetooth_sig.gatt.services.ServiceName) -> src.bluetooth_sig.types.uuid.BluetoothUUID | None
      :abstractmethod:


      Get the UUID for a service name or enum.



   .. py:method:: get_characteristic_info_by_name(name: src.bluetooth_sig.gatt.characteristics.CharacteristicName) -> Any | None

      Get characteristic info by enum name (optional method).



