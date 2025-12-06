src.bluetooth_sig.core.translator
=================================

.. py:module:: src.bluetooth_sig.core.translator

.. autoapi-nested-parse::

   Core Bluetooth SIG standards translator functionality.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.core.translator.BluetoothSIG
   src.bluetooth_sig.core.translator.CharacteristicDataDict
   src.bluetooth_sig.core.translator.logger


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.core.translator.BluetoothSIGTranslator


Module Contents
---------------

.. py:class:: BluetoothSIGTranslator

   Pure Bluetooth SIG standards translator for characteristic and service interpretation.

   This class provides the primary API surface for Bluetooth SIG standards translation,
   covering characteristic parsing, service discovery, UUID resolution, and registry
   management.

   Singleton Pattern:
       This class is implemented as a singleton to provide a global registry for
       custom characteristics and services. Access the singleton instance using
       `BluetoothSIGTranslator.get_instance()` or the module-level `translator` variable.

   Key features:
   - Parse raw BLE characteristic data using Bluetooth SIG specifications
   - Resolve UUIDs to [CharacteristicInfo][bluetooth_sig.types.CharacteristicInfo]
     and [ServiceInfo][bluetooth_sig.types.ServiceInfo]
   - Create BaseGattService instances from service UUIDs
   - Access comprehensive registry of supported characteristics and services

   Note: This class intentionally has >20 public methods as it serves as the
   primary API surface for Bluetooth SIG standards translation. The methods are
   organized by functionality and reducing them would harm API clarity.

   Initialize the SIG translator (singleton pattern).


   .. py:method:: clear_services() -> None

      Clear all discovered services.



   .. py:method:: get_characteristic_info_by_name(name: src.bluetooth_sig.types.gatt_enums.CharacteristicName) -> src.bluetooth_sig.types.CharacteristicInfo | None

      Get characteristic info by enum name.

      :param name: CharacteristicName enum

      :returns: CharacteristicInfo if found, None otherwise



   .. py:method:: get_characteristic_info_by_uuid(uuid: str) -> src.bluetooth_sig.types.CharacteristicInfo | None

      Get information about a characteristic by UUID.

      Retrieve metadata for a Bluetooth characteristic using its UUID. This includes
      the characteristic's name, description, value type, unit, and properties.

      :param uuid: The characteristic UUID (16-bit short form or full 128-bit)

      :returns: [CharacteristicInfo][bluetooth_sig.CharacteristicInfo] with metadata or None if not found

      .. admonition:: Example

         Get battery level characteristic info:
         
         ```python
         from bluetooth_sig import BluetoothSIGTranslator
         
         translator = BluetoothSIGTranslator()
         info = translator.get_characteristic_info_by_uuid("2A19")
         if info:
             print(f"Name: {info.name}")  # Name: Battery Level
         ```



   .. py:method:: get_characteristic_uuid_by_name(name: src.bluetooth_sig.types.gatt_enums.CharacteristicName) -> src.bluetooth_sig.types.uuid.BluetoothUUID | None

      Get the UUID for a characteristic name enum.

      :param name: CharacteristicName enum

      :returns: Characteristic UUID or None if not found



   .. py:method:: get_characteristics_info_by_uuids(uuids: list[str]) -> dict[str, src.bluetooth_sig.types.CharacteristicInfo | None]

      Get information about multiple characteristics by UUID.

      :param uuids: List of characteristic UUIDs

      :returns: Dictionary mapping UUIDs to CharacteristicInfo
                (or None if not found)



   .. py:method:: get_instance() -> BluetoothSIGTranslator
      :classmethod:


      Get the singleton instance of BluetoothSIGTranslator.

      :returns: The singleton BluetoothSIGTranslator instance

      .. admonition:: Example

         ```python
         from bluetooth_sig import BluetoothSIGTranslator
         
         # Get the singleton instance
         translator = BluetoothSIGTranslator.get_instance()
         ```



   .. py:method:: get_service_by_uuid(uuid: str) -> src.bluetooth_sig.gatt.services.base.BaseGattService | None

      Get a service instance by UUID.

      :param uuid: The service UUID

      :returns: Service instance if found, None otherwise



   .. py:method:: get_service_characteristics(service_uuid: str) -> list[str]

      Get the characteristic UUIDs associated with a service.

      :param service_uuid: The service UUID

      :returns: List of characteristic UUIDs for this service



   .. py:method:: get_service_info_by_name(name: str) -> src.bluetooth_sig.types.ServiceInfo | None

      Get service info by name instead of UUID.

      :param name: Service name

      :returns: ServiceInfo if found, None otherwise



   .. py:method:: get_service_info_by_uuid(uuid: str) -> src.bluetooth_sig.types.ServiceInfo | None

      Get information about a service by UUID.

      :param uuid: The service UUID

      :returns: ServiceInfo with metadata or None if not found



   .. py:method:: get_service_uuid_by_name(name: str | src.bluetooth_sig.gatt.services.ServiceName) -> src.bluetooth_sig.types.uuid.BluetoothUUID | None

      Get the UUID for a service name or enum.

      :param name: Service name or enum

      :returns: Service UUID or None if not found



   .. py:method:: get_sig_info_by_name(name: str) -> src.bluetooth_sig.types.SIGInfo | None

      Get Bluetooth SIG information for a characteristic or service by name.

      :param name: Characteristic or service name

      :returns: CharacteristicInfo or ServiceInfo if found, None otherwise



   .. py:method:: get_sig_info_by_uuid(uuid: str) -> src.bluetooth_sig.types.SIGInfo | None

      Get Bluetooth SIG information for a UUID.

      :param uuid: UUID string (with or without dashes)

      :returns: CharacteristicInfo or ServiceInfo if found, None otherwise



   .. py:method:: list_supported_characteristics() -> dict[str, str]

      List all supported characteristics with their names and UUIDs.

      :returns: Dictionary mapping characteristic names to UUIDs



   .. py:method:: list_supported_services() -> dict[str, str]

      List all supported services with their names and UUIDs.

      :returns: Dictionary mapping service names to UUIDs



   .. py:method:: parse_characteristic(uuid: str, raw_data: bytes | bytearray, ctx: src.bluetooth_sig.types.CharacteristicContext | None = None) -> src.bluetooth_sig.gatt.characteristics.base.CharacteristicData

      Parse a characteristic's raw data using Bluetooth SIG standards.

      :param uuid: The characteristic UUID (with or without dashes)
      :param raw_data: Raw bytes from the characteristic (bytes or bytearray)
      :param ctx: Optional CharacteristicContext providing device-level info

      :returns: CharacteristicData with parsed value and metadata

      .. admonition:: Example

         Parse battery level data:
         
         ```python
         from bluetooth_sig import BluetoothSIGTranslator
         
         translator = BluetoothSIGTranslator()
         result = translator.parse_characteristic("2A19", b"\x64")
         print(f"Battery: {result.value}%")  # Battery: 100%
         ```



   .. py:method:: parse_characteristic_async(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID, raw_data: bytes, ctx: src.bluetooth_sig.types.CharacteristicContext | None = None) -> src.bluetooth_sig.gatt.characteristics.base.CharacteristicData
      :async:


      Parse characteristic data in an async-compatible manner.

      This is an async wrapper that allows characteristic parsing to be used
      in async contexts. The actual parsing is performed synchronously as it's
      a fast, CPU-bound operation that doesn't benefit from async I/O.

      :param uuid: The characteristic UUID (string or BluetoothUUID)
      :param raw_data: Raw bytes from the characteristic
      :param ctx: Optional context providing device-level info

      :returns: CharacteristicData with parsed value and metadata

      .. admonition:: Example

         ```python
         async with BleakClient(address) as client:
             data = await client.read_gatt_char("2A19")
             result = await translator.parse_characteristic_async("2A19", data)
             print(f"Battery: {result.value}%")
         ```



   .. py:method:: parse_characteristics(char_data: dict[str, bytes], ctx: src.bluetooth_sig.types.CharacteristicContext | None = None) -> dict[str, src.bluetooth_sig.gatt.characteristics.base.CharacteristicData]

      Parse multiple characteristics at once with dependency-aware ordering.

      This method automatically handles multi-characteristic dependencies by parsing
      independent characteristics first, then parsing characteristics that depend on them.
      The parsing order is determined by the `required_dependencies` and `optional_dependencies`
      attributes declared on characteristic classes.

      Required dependencies MUST be present and successfully parsed; missing required
      dependencies result in parse failure with MissingDependencyError. Optional dependencies
      enrich parsing when available but are not mandatory.

      :param char_data: Dictionary mapping UUIDs to raw data bytes
      :param ctx: Optional CharacteristicContext used as the starting context

      :returns: Dictionary mapping UUIDs to CharacteristicData results

      :raises ValueError: If circular dependencies are detected

      .. admonition:: Example

         Parse multiple environmental characteristics:
         
         ```python
         from bluetooth_sig import BluetoothSIGTranslator
         
         translator = BluetoothSIGTranslator()
         data = {
             "2A6E": b"\\x0A\\x00",  # Temperature
             "2A6F": b"\\x32\\x00",  # Humidity
         }
         results = translator.parse_characteristics(data)
         for uuid, result in results.items():
             print(f"{uuid}: {result.value}")
         ```



   .. py:method:: parse_characteristics_async(char_data: dict[str, bytes], ctx: src.bluetooth_sig.types.CharacteristicContext | None = None) -> dict[str, src.bluetooth_sig.gatt.characteristics.base.CharacteristicData]
      :async:


      Parse multiple characteristics in an async-compatible manner.

      This is an async wrapper for batch characteristic parsing. The parsing
      is performed synchronously as it's a fast, CPU-bound operation. This method
      allows batch parsing to be used naturally in async workflows.

      :param char_data: Dictionary mapping UUIDs to raw data bytes
      :param ctx: Optional context

      :returns: Dictionary mapping UUIDs to CharacteristicData results

      .. admonition:: Example

         ```python
         async with BleakClient(address) as client:
             # Read multiple characteristics
             char_data = {}
             for uuid in ["2A19", "2A6E", "2A6F"]:
                 char_data[uuid] = await client.read_gatt_char(uuid)
         
             # Parse all asynchronously
             results = await translator.parse_characteristics_async(char_data)
             for uuid, result in results.items():
                 print(f"{uuid}: {result.value}")
         ```



   .. py:method:: process_services(services: dict[str, dict[str, CharacteristicDataDict]]) -> None

      Process discovered services and their characteristics.

      :param services: Dictionary of service UUIDs to their characteristics



   .. py:method:: register_custom_characteristic_class(uuid_or_name: str, cls: type[src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic], info: src.bluetooth_sig.types.CharacteristicInfo | None = None, override: bool = False) -> None

      Register a custom characteristic class at runtime.

      :param uuid_or_name: The characteristic UUID or name
      :param cls: The characteristic class to register
      :param info: Optional CharacteristicInfo with metadata (name, unit, value_type)
      :param override: Whether to override existing registrations

      :raises TypeError: If cls does not inherit from BaseCharacteristic
      :raises ValueError: If UUID conflicts with existing registration and override=False

      .. admonition:: Example

         ```python
         from bluetooth_sig import BluetoothSIGTranslator, CharacteristicInfo, ValueType
         from bluetooth_sig.types import BluetoothUUID
         
         translator = BluetoothSIGTranslator()
         info = CharacteristicInfo(
             uuid=BluetoothUUID("12345678-1234-1234-1234-123456789abc"),
             name="Custom Temperature",
             unit="°C",
             value_type=ValueType.FLOAT,
         )
         translator.register_custom_characteristic_class(str(info.uuid), MyCustomCharacteristic, info=info)
         ```



   .. py:method:: register_custom_service_class(uuid_or_name: str, cls: type[src.bluetooth_sig.gatt.services.base.BaseGattService], info: src.bluetooth_sig.types.ServiceInfo | None = None, override: bool = False) -> None

      Register a custom service class at runtime.

      :param uuid_or_name: The service UUID or name
      :param cls: The service class to register
      :param info: Optional ServiceInfo with metadata (name)
      :param override: Whether to override existing registrations

      :raises TypeError: If cls does not inherit from BaseGattService
      :raises ValueError: If UUID conflicts with existing registration and override=False

      .. admonition:: Example

         ```python
         from bluetooth_sig import BluetoothSIGTranslator, ServiceInfo
         from bluetooth_sig.types import BluetoothUUID
         
         translator = BluetoothSIGTranslator()
         info = ServiceInfo(uuid=BluetoothUUID("12345678-1234-1234-1234-123456789abc"), name="Custom Service")
         translator.register_custom_service_class(str(info.uuid), MyCustomService, info=info)
         ```



   .. py:method:: validate_characteristic_data(uuid: str, data: bytes) -> src.bluetooth_sig.types.ValidationResult

      Validate characteristic data format against SIG specifications.

      :param uuid: The characteristic UUID
      :param data: Raw data bytes to validate

      :returns: ValidationResult with validation details



   .. py:property:: discovered_services
      :type: list[src.bluetooth_sig.gatt.services.base.BaseGattService]


      Get list of discovered service instances.

      :returns: List of discovered service instances


.. py:data:: BluetoothSIG

.. py:data:: CharacteristicDataDict

.. py:data:: logger

