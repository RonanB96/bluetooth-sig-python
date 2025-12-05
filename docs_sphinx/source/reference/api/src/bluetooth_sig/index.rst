src.bluetooth_sig
=================

.. py:module:: src.bluetooth_sig

.. autoapi-nested-parse::

   Bluetooth SIG Standards Library for pure SIG standard interpretation.

   A framework-agnostic library for parsing and interpreting Bluetooth SIG
   standards, including GATT characteristics, services, and UUID
   resolution.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /reference/api/src/bluetooth_sig/core/index
   /reference/api/src/bluetooth_sig/device/index
   /reference/api/src/bluetooth_sig/gatt/index
   /reference/api/src/bluetooth_sig/registry/index
   /reference/api/src/bluetooth_sig/stream/index
   /reference/api/src/bluetooth_sig/types/index
   /reference/api/src/bluetooth_sig/utils/index


Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.members_registry


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.AsyncParsingSession
   src.bluetooth_sig.BluetoothSIGTranslator
   src.bluetooth_sig.BaseCharacteristic
   src.bluetooth_sig.BaseGattService
   src.bluetooth_sig.CharacteristicRegistry
   src.bluetooth_sig.CharacteristicData
   src.bluetooth_sig.GattServiceRegistry
   src.bluetooth_sig.CharacteristicInfo
   src.bluetooth_sig.ServiceInfo
   src.bluetooth_sig.SIGInfo
   src.bluetooth_sig.ValidationResult


Package Contents
----------------

.. py:class:: AsyncParsingSession(translator: src.bluetooth_sig.core.translator.BluetoothSIGTranslator, ctx: src.bluetooth_sig.types.CharacteristicContext | None = None)

   Async context manager for parsing sessions.

   Maintains parsing context across multiple async operations.

   .. admonition:: Example

      ```python
      async with AsyncParsingSession() as session:
          result1 = await session.parse("2A19", data1)
          result2 = await session.parse("2A6E", data2)
          # Context automatically shared between parses
      ```


   .. py:attribute:: translator


   .. py:attribute:: context
      :value: None



   .. py:attribute:: results
      :type:  dict[str, src.bluetooth_sig.gatt.characteristics.base.CharacteristicData]


   .. py:method:: parse(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID, data: bytes) -> src.bluetooth_sig.gatt.characteristics.base.CharacteristicData
      :async:


      Parse characteristic with accumulated context.

      :param uuid: Characteristic UUID
      :param data: Raw bytes

      :returns: CharacteristicData



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



   .. py:method:: get_service_uuid_by_name(name: str | src.bluetooth_sig.gatt.services.ServiceName) -> src.bluetooth_sig.types.uuid.BluetoothUUID | None

      Get the UUID for a service name or enum.

      :param name: Service name or enum

      :returns: Service UUID or None if not found



   .. py:method:: get_characteristic_info_by_name(name: src.bluetooth_sig.types.gatt_enums.CharacteristicName) -> src.bluetooth_sig.types.CharacteristicInfo | None

      Get characteristic info by enum name.

      :param name: CharacteristicName enum

      :returns: CharacteristicInfo if found, None otherwise



   .. py:method:: get_service_info_by_name(name: str) -> src.bluetooth_sig.types.ServiceInfo | None

      Get service info by name instead of UUID.

      :param name: Service name

      :returns: ServiceInfo if found, None otherwise



   .. py:method:: get_service_info_by_uuid(uuid: str) -> src.bluetooth_sig.types.ServiceInfo | None

      Get information about a service by UUID.

      :param uuid: The service UUID

      :returns: ServiceInfo with metadata or None if not found



   .. py:method:: list_supported_characteristics() -> dict[str, str]

      List all supported characteristics with their names and UUIDs.

      :returns: Dictionary mapping characteristic names to UUIDs



   .. py:method:: list_supported_services() -> dict[str, str]

      List all supported services with their names and UUIDs.

      :returns: Dictionary mapping service names to UUIDs



   .. py:method:: process_services(services: dict[str, dict[str, CharacteristicDataDict]]) -> None

      Process discovered services and their characteristics.

      :param services: Dictionary of service UUIDs to their characteristics



   .. py:method:: get_service_by_uuid(uuid: str) -> src.bluetooth_sig.gatt.services.base.BaseGattService | None

      Get a service instance by UUID.

      :param uuid: The service UUID

      :returns: Service instance if found, None otherwise



   .. py:property:: discovered_services
      :type: list[src.bluetooth_sig.gatt.services.base.BaseGattService]


      Get list of discovered service instances.

      :returns: List of discovered service instances


   .. py:method:: clear_services() -> None

      Clear all discovered services.



   .. py:method:: get_sig_info_by_name(name: str) -> src.bluetooth_sig.types.SIGInfo | None

      Get Bluetooth SIG information for a characteristic or service by name.

      :param name: Characteristic or service name

      :returns: CharacteristicInfo or ServiceInfo if found, None otherwise



   .. py:method:: get_sig_info_by_uuid(uuid: str) -> src.bluetooth_sig.types.SIGInfo | None

      Get Bluetooth SIG information for a UUID.

      :param uuid: UUID string (with or without dashes)

      :returns: CharacteristicInfo or ServiceInfo if found, None otherwise



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



   .. py:method:: get_characteristics_info_by_uuids(uuids: list[str]) -> dict[str, src.bluetooth_sig.types.CharacteristicInfo | None]

      Get information about multiple characteristics by UUID.

      :param uuids: List of characteristic UUIDs

      :returns: Dictionary mapping UUIDs to CharacteristicInfo
                (or None if not found)



   .. py:method:: validate_characteristic_data(uuid: str, data: bytes) -> src.bluetooth_sig.types.ValidationResult

      Validate characteristic data format against SIG specifications.

      :param uuid: The characteristic UUID
      :param data: Raw data bytes to validate

      :returns: ValidationResult with validation details



   .. py:method:: get_service_characteristics(service_uuid: str) -> list[str]

      Get the characteristic UUIDs associated with a service.

      :param service_uuid: The service UUID

      :returns: List of characteristic UUIDs for this service



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



.. py:class:: BaseCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`abc.ABC`


   Base class for all GATT characteristics.

   Automatically resolves UUID, unit, and value_type from Bluetooth SIG YAML specifications.
   Supports manual overrides via _manual_unit and _manual_value_type attributes.

   Note: This class intentionally has >20 public methods as it provides the complete
   characteristic API including parsing, validation, UUID resolution, registry interaction,
   and metadata access. The methods are well-organized by functionality.

   Validation Attributes (optional class-level declarations):
       min_value: Minimum allowed value for parsed data
       max_value: Maximum allowed value for parsed data
       expected_length: Exact expected data length in bytes
       min_length: Minimum required data length in bytes
       max_length: Maximum allowed data length in bytes
       allow_variable_length: Whether variable length data is acceptable
       expected_type: Expected Python type for parsed values

   Example usage in subclasses:
       class ExampleCharacteristic(BaseCharacteristic):
           '''Example showing validation attributes usage.'''

           # Declare validation constraints as class attributes
           expected_length = 2
           min_value = 0
           max_value = 65535  # UINT16_MAX
           expected_type = int

           def decode_value(self, data: bytearray) -> int:
               # Just parse - validation happens automatically in parse_value
               return DataParser.parse_int16(data, 0, signed=False)

       # Before: BatteryLevelCharacteristic with hardcoded validation
       # class BatteryLevelCharacteristic(BaseCharacteristic):
       #     def decode_value(self, data: bytearray) -> int:
       #         if not data:
       #             raise ValueError("Battery level data must be at least 1 byte")
       #         level = data[0]
       #         if not 0 <= level <= PERCENTAGE_MAX:
       #             raise ValueError(f"Battery level must be 0-100, got {level}")
       #         return level

       # After: BatteryLevelCharacteristic with declarative validation
       # class BatteryLevelCharacteristic(BaseCharacteristic):
       #     expected_length = 1
       #     min_value = 0
       #     max_value = 100  # PERCENTAGE_MAX
       #     expected_type = int
       #
       #     def decode_value(self, data: bytearray) -> int:
       #         return data[0]  # Validation happens automatically


   .. py:attribute:: min_value
      :type:  int | float | None
      :value: None



   .. py:attribute:: max_value
      :type:  int | float | None
      :value: None



   .. py:attribute:: expected_length
      :type:  int | None
      :value: None



   .. py:attribute:: min_length
      :type:  int | None
      :value: None



   .. py:attribute:: max_length
      :type:  int | None
      :value: None



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: False



   .. py:attribute:: expected_type
      :type:  type | None
      :value: None



   .. py:attribute:: properties
      :type:  list[src.bluetooth_sig.types.gatt_enums.GattProperty]
      :value: None



   .. py:attribute:: value_type
      :type:  src.bluetooth_sig.types.gatt_enums.ValueType


   .. py:attribute:: last_parsed
      :type:  CharacteristicData | None
      :value: None



   .. py:property:: uuid
      :type: src.bluetooth_sig.types.uuid.BluetoothUUID


      Get the characteristic UUID from _info.


   .. py:property:: info
      :type: src.bluetooth_sig.types.CharacteristicInfo


      Characteristic information.


   .. py:property:: spec
      :type: src.bluetooth_sig.gatt.uuid_registry.CharacteristicSpec | None


      Get the full GSS specification with description and detailed metadata.


   .. py:property:: name
      :type: str


      Get the characteristic name from _info.


   .. py:property:: description
      :type: str


      Get the characteristic description from GSS specification.


   .. py:property:: display_name
      :type: str


      Get the display name for this characteristic.

      Uses explicit _characteristic_name if set, otherwise falls back
      to class name.


   .. py:property:: required_dependencies
      :type: list[str]


      Get resolved required dependency UUID strings.


   .. py:property:: optional_dependencies
      :type: list[str]


      Get resolved optional dependency UUID strings.


   .. py:method:: get_allows_sig_override() -> bool
      :classmethod:


      Check if this characteristic class allows overriding SIG characteristics.

      Custom characteristics that need to override official Bluetooth SIG
      characteristics must set _allows_sig_override = True as a class attribute.

      :returns: True if SIG override is allowed, False otherwise.



   .. py:method:: get_configured_info() -> src.bluetooth_sig.types.CharacteristicInfo | None
      :classmethod:


      Get the class-level configured CharacteristicInfo.

      This provides public access to the _configured_info attribute that is set
      by __init_subclass__ for custom characteristics.

      :returns: CharacteristicInfo if configured, None otherwise



   .. py:method:: get_class_uuid() -> src.bluetooth_sig.types.uuid.BluetoothUUID | None
      :classmethod:


      Get the characteristic UUID for this class without creating an instance.

      This is the public API for registry and other modules to resolve UUIDs.

      :returns: BluetoothUUID if the class has a resolvable UUID, None otherwise.



   .. py:method:: matches_uuid(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID) -> bool
      :classmethod:


      Check if this characteristic matches the given UUID.



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> Any

      Parse the characteristic's raw value.

      If _template is set, uses the template's decode_value method.
      Otherwise, subclasses must override this method.

      :param data: Raw bytes from the characteristic read
      :param ctx: Optional context information for parsing

      :returns: Parsed value in the appropriate type

      :raises NotImplementedError: If no template is set and subclass doesn't override



   .. py:method:: get_context_characteristic(ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None, characteristic_name: src.bluetooth_sig.types.gatt_enums.CharacteristicName | str | type[BaseCharacteristic]) -> src.bluetooth_sig.types.CharacteristicDataProtocol | None

      Find a characteristic in a context by name or class.

      :param ctx: Context containing other characteristics.
      :param characteristic_name: Enum, string name, or characteristic class.

      :returns: Characteristic data if found, None otherwise.



   .. py:method:: parse_value(data: bytes | bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> CharacteristicData

      Parse raw characteristic data into structured value with validation.

      :param data: Raw bytes from the characteristic read
      :param ctx: Optional context with device info and other characteristics

      :returns: CharacteristicData with parsed value (stored in self.last_parsed)



   .. py:method:: encode_value(data: Any) -> bytearray

      Encode the characteristic's value to raw bytes.

      If _template is set, uses the template's encode_value method.
      Otherwise, subclasses must override this method.

      This is a low-level method that performs no validation. For encoding
      with validation, use encode() instead.

      :param data: Dataclass instance or value to encode

      :returns: Encoded bytes for characteristic write

      :raises ValueError: If data is invalid for encoding
      :raises NotImplementedError: If no template is set and subclass doesn't override



   .. py:method:: build_value(data: Any) -> bytearray

      Build characteristic bytes from value with validation.

      High-level encoding method that validates before encoding, mirroring
      how parse_value() validates after decode_value().

      :param data: Value to encode (type depends on characteristic)

      :returns: Validated and encoded bytes for characteristic write

      :raises ValueError: If data fails validation
      :raises TypeError: If data type is incorrect
      :raises NotImplementedError: If characteristic doesn't support encoding



   .. py:property:: unit
      :type: str


      Get the unit of measurement from _info.

      Returns empty string for characteristics without units (e.g., bitfields).


   .. py:property:: size
      :type: int | None


      Get the size in bytes for this characteristic from YAML specifications.

      Returns the field size from YAML automation if available, otherwise None.
      This is useful for determining the expected data length for parsing
      and encoding.


   .. py:property:: value_type_resolved
      :type: src.bluetooth_sig.types.gatt_enums.ValueType


      Get the value type from _info.


   .. py:method:: get_yaml_data_type() -> str | None

      Get the data type from YAML automation (e.g., 'sint16', 'uint8').



   .. py:method:: get_yaml_field_size() -> int | None

      Get the field size in bytes from YAML automation.



   .. py:method:: get_yaml_unit_id() -> str | None

      Get the Bluetooth SIG unit identifier from YAML automation.



   .. py:method:: get_yaml_resolution_text() -> str | None

      Get the resolution description text from YAML automation.



   .. py:method:: is_signed_from_yaml() -> bool

      Determine if the data type is signed based on YAML automation.



   .. py:method:: add_descriptor(descriptor: src.bluetooth_sig.gatt.descriptors.BaseDescriptor) -> None

      Add a descriptor to this characteristic.

      :param descriptor: The descriptor instance to add



   .. py:method:: get_descriptor(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID) -> src.bluetooth_sig.gatt.descriptors.BaseDescriptor | None

      Get a descriptor by UUID.

      :param uuid: Descriptor UUID (string or BluetoothUUID)

      :returns: Descriptor instance if found, None otherwise



   .. py:method:: get_descriptors() -> dict[str, src.bluetooth_sig.gatt.descriptors.BaseDescriptor]

      Get all descriptors for this characteristic.

      :returns: Dict mapping descriptor UUID strings to descriptor instances



   .. py:method:: get_cccd() -> src.bluetooth_sig.gatt.descriptors.BaseDescriptor | None

      Get the Client Characteristic Configuration Descriptor (CCCD).

      :returns: CCCD descriptor instance if present, None otherwise



   .. py:method:: can_notify() -> bool

      Check if this characteristic supports notifications.

      :returns: True if the characteristic has a CCCD descriptor, False otherwise



   .. py:method:: get_descriptor_from_context(ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None, descriptor_class: type[src.bluetooth_sig.gatt.descriptors.BaseDescriptor]) -> src.bluetooth_sig.types.registry.descriptor_types.DescriptorData | None

      Get a descriptor of the specified type from the context.

      :param ctx: Characteristic context containing descriptors
      :param descriptor_class: The descriptor class to look for (e.g., ValidRangeDescriptor)

      :returns: DescriptorData if found, None otherwise



   .. py:method:: get_valid_range_from_context(ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> tuple[int | float, int | float] | None

      Get valid range from descriptor context if available.

      :param ctx: Characteristic context containing descriptors

      :returns: Tuple of (min, max) values if Valid Range descriptor present, None otherwise



   .. py:method:: get_presentation_format_from_context(ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> src.bluetooth_sig.gatt.descriptors.characteristic_presentation_format.CharacteristicPresentationFormatData | None

      Get presentation format from descriptor context if available.

      :param ctx: Characteristic context containing descriptors

      :returns: CharacteristicPresentationFormatData if present, None otherwise



   .. py:method:: get_user_description_from_context(ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> str | None

      Get user description from descriptor context if available.

      :param ctx: Characteristic context containing descriptors

      :returns: User description string if present, None otherwise



   .. py:method:: validate_value_against_descriptor_range(value: int | float, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> bool

      Validate a value against descriptor-defined valid range.

      :param value: Value to validate
      :param ctx: Characteristic context containing descriptors

      :returns: True if value is within valid range or no range defined, False otherwise



   .. py:method:: enhance_error_message_with_descriptors(base_message: str, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> str

      Enhance error message with descriptor information for better debugging.

      :param base_message: Original error message
      :param ctx: Characteristic context containing descriptors

      :returns: Enhanced error message with descriptor context



   .. py:method:: get_byte_order_hint() -> str

      Get byte order hint (Bluetooth SIG uses little-endian by convention).



.. py:class:: BaseGattService(info: src.bluetooth_sig.types.ServiceInfo | None = None, validation: ServiceValidationConfig | None = None)

   Base class for all GATT services.

   Automatically resolves UUID, name, and summary from Bluetooth SIG specifications.
   Follows the same pattern as BaseCharacteristic for consistency.


   .. py:attribute:: characteristics
      :type:  dict[src.bluetooth_sig.types.uuid.BluetoothUUID, src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


   .. py:property:: uuid
      :type: src.bluetooth_sig.types.uuid.BluetoothUUID


      Get the service UUID from _info.


   .. py:property:: name
      :type: str


      Get the service name from _info.


   .. py:property:: info
      :type: src.bluetooth_sig.types.ServiceInfo


      Return the resolved service information for this instance.

      The info property provides all metadata about the service, including UUID, name, and description.


   .. py:method:: get_class_uuid() -> src.bluetooth_sig.types.uuid.BluetoothUUID
      :classmethod:


      Get the UUID for this service class without instantiation.

      :returns: BluetoothUUID for this service class

      :raises UUIDResolutionError: If UUID cannot be resolved



   .. py:method:: get_name() -> str
      :classmethod:


      Get the service name for this class without creating an instance.

      :returns: The service name as registered in the UUID registry.



   .. py:method:: matches_uuid(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID) -> bool
      :classmethod:


      Check if this service matches the given UUID.



   .. py:method:: get_expected_characteristics() -> ServiceCharacteristicCollection
      :classmethod:


      Get the expected characteristics for this service from the service_characteristics dict.

      Looks for a 'service_characteristics' class attribute containing a dictionary of
          CharacteristicName -> required flag, and automatically builds CharacteristicSpec objects.

      :returns: ServiceCharacteristicCollection mapping characteristic name to CharacteristicSpec



   .. py:method:: get_required_characteristics() -> ServiceCharacteristicCollection
      :classmethod:


      Get the required characteristics for this service from the characteristics dict.

      Automatically filters the characteristics dictionary for required=True entries.

      :returns: ServiceCharacteristicCollection mapping characteristic name to CharacteristicSpec



   .. py:method:: get_characteristics_schema() -> type | None
      :classmethod:


      Get the TypedDict schema for this service's characteristics.

      Override this method to provide strong typing for characteristics.
      If not implemented, falls back to get_expected_characteristics().

      :returns: TypedDict class defining the service's characteristics, or None



   .. py:method:: get_required_characteristic_keys() -> set[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName]
      :classmethod:


      Get the set of required characteristic keys from the schema.

      Override this method when using strongly-typed characteristics.
      If not implemented, falls back to get_required_characteristics().keys().

      :returns: Set of required characteristic field names



   .. py:method:: get_expected_characteristic_uuids() -> set[src.bluetooth_sig.types.uuid.BluetoothUUID]

      Get the set of expected characteristic UUIDs for this service.



   .. py:method:: get_required_characteristic_uuids() -> set[src.bluetooth_sig.types.uuid.BluetoothUUID]

      Get the set of required characteristic UUIDs for this service.



   .. py:method:: process_characteristics(characteristics: src.bluetooth_sig.types.gatt_services.ServiceDiscoveryData) -> None

      Process the characteristics for this service (default implementation).

      :param characteristics: Dict mapping UUID to characteristic info



   .. py:method:: get_characteristic(uuid: src.bluetooth_sig.types.uuid.BluetoothUUID) -> GattCharacteristic | None

      Get a characteristic by UUID.



   .. py:property:: supported_characteristics
      :type: set[src.bluetooth_sig.gatt.characteristics.BaseCharacteristic]


      Get the set of characteristic UUIDs supported by this service.


   .. py:method:: get_optional_characteristics() -> ServiceCharacteristicCollection
      :classmethod:


      Get the optional characteristics for this service by name and class.

      :returns: ServiceCharacteristicCollection mapping characteristic name to CharacteristicSpec



   .. py:method:: get_conditional_characteristics() -> ServiceCharacteristicCollection
      :classmethod:


      Get characteristics that are required only under certain conditions.

      :returns: ServiceCharacteristicCollection mapping characteristic name to CharacteristicSpec

      Override in subclasses to specify conditional characteristics.




   .. py:method:: validate_bluetooth_sig_compliance() -> list[str]
      :classmethod:


      Validate compliance with Bluetooth SIG service specification.

      :returns: List of compliance issues found

      Override in subclasses to provide service-specific validation.




   .. py:method:: validate_service(strict: bool = False) -> ServiceValidationResult

      Validate the completeness and health of this service.

      :param strict: If True, missing optional characteristics are treated as warnings

      :returns: ServiceValidationResult with detailed status information



   .. py:method:: get_missing_characteristics() -> dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, ServiceCharacteristicInfo]

      Get detailed information about missing characteristics.

      :returns: Dict mapping characteristic name to ServiceCharacteristicInfo



   .. py:method:: get_characteristic_status(characteristic_name: src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName) -> ServiceCharacteristicInfo | None

      Get detailed status of a specific characteristic.

      :param characteristic_name: CharacteristicName enum

      :returns: CharacteristicInfo if characteristic is expected by this service, None otherwise



   .. py:method:: get_service_completeness_report() -> ServiceCompletenessReport

      Get a comprehensive report about service completeness.

      :returns: ServiceCompletenessReport with detailed service status information



   .. py:method:: has_minimum_functionality() -> bool

      Check if service has minimum required functionality.

      :returns: True if service has all required characteristics and is usable



.. py:class:: CharacteristicRegistry

   Bases: :py:obj:`src.bluetooth_sig.registry.base.BaseUUIDClassRegistry`\ [\ :py:obj:`src.bluetooth_sig.types.gatt_enums.CharacteristicName`\ , :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`\ ]


   Encapsulates all GATT characteristic registry operations.


   .. py:method:: register_characteristic_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int, char_cls: type[src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic], override: bool = False) -> None
      :classmethod:


      Register a custom characteristic class at runtime.

      Backward compatibility wrapper for register_class().



   .. py:method:: unregister_characteristic_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> None
      :classmethod:


      Unregister a custom characteristic class.

      Backward compatibility wrapper for unregister_class().



   .. py:method:: get_characteristic_class(name: src.bluetooth_sig.types.gatt_enums.CharacteristicName) -> type[src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic] | None
      :classmethod:


      Get the characteristic class for a given CharacteristicName enum.

      Backward compatibility wrapper for get_class_by_enum().



   .. py:method:: get_characteristic_class_by_uuid(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> type[src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic] | None
      :classmethod:


      Get the characteristic class for a given UUID.

      Backward compatibility wrapper for get_class_by_uuid().



   .. py:method:: create_characteristic(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic | None
      :classmethod:


      Create a characteristic instance from a UUID.

      :param uuid: The characteristic UUID (string, BluetoothUUID, or int)

      :returns: Characteristic instance if found, None if UUID not registered

      :raises ValueError: If uuid format is invalid



   .. py:method:: list_all_characteristic_names() -> list[str]
      :staticmethod:


      List all supported characteristic names as strings.



   .. py:method:: list_all_characteristic_enums() -> list[src.bluetooth_sig.types.gatt_enums.CharacteristicName]
      :staticmethod:


      List all supported characteristic names as enum values.



   .. py:method:: get_all_characteristics() -> dict[src.bluetooth_sig.types.gatt_enums.CharacteristicName, type[src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic]]
      :classmethod:


      Get all registered characteristic classes.



   .. py:method:: clear_custom_registrations() -> None
      :classmethod:


      Clear all custom characteristic registrations (for testing).



   .. py:method:: clear_cache() -> None
      :classmethod:


      Clear the characteristic class map cache (for testing).



.. py:class:: CharacteristicData

   Bases: :py:obj:`msgspec.Struct`


   Parse result container with back-reference to characteristic.

   .. attribute:: characteristic

      The BaseCharacteristic instance that parsed this data

   .. attribute:: value

      Parsed and validated value

   .. attribute:: raw_data

      Original raw bytes

   .. attribute:: parse_success

      Whether parsing succeeded

   .. attribute:: error_message

      Error description if parse failed

   .. attribute:: field_errors

      Field-level parsing errors

   .. attribute:: parse_trace

      Detailed parsing steps for debugging


   .. py:attribute:: characteristic
      :type:  BaseCharacteristic


   .. py:attribute:: value
      :type:  Any | None
      :value: None



   .. py:attribute:: raw_data
      :type:  bytes
      :value: b''



   .. py:attribute:: parse_success
      :type:  bool
      :value: False



   .. py:attribute:: error_message
      :type:  str
      :value: ''



   .. py:attribute:: field_errors
      :type:  list[src.bluetooth_sig.types.ParseFieldError]


   .. py:attribute:: parse_trace
      :type:  list[str]


   .. py:property:: info
      :type: src.bluetooth_sig.types.CharacteristicInfo


      Characteristic metadata.


   .. py:property:: name
      :type: str


      Characteristic name.


   .. py:property:: uuid
      :type: src.bluetooth_sig.types.uuid.BluetoothUUID


      Characteristic UUID.


   .. py:property:: unit
      :type: str


      Unit of measurement.


   .. py:property:: properties
      :type: list[src.bluetooth_sig.types.gatt_enums.GattProperty]


      BLE GATT properties.


.. py:class:: GattServiceRegistry

   Bases: :py:obj:`src.bluetooth_sig.registry.base.BaseUUIDClassRegistry`\ [\ :py:obj:`src.bluetooth_sig.types.gatt_enums.ServiceName`\ , :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`\ ]


   Registry for all supported GATT services.


   .. py:method:: register_service_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int, service_cls: type[src.bluetooth_sig.gatt.services.base.BaseGattService], override: bool = False) -> None
      :classmethod:


      Register a custom service class at runtime.

      :param uuid: The service UUID
      :param service_cls: The service class to register
      :param override: Whether to override existing registrations

      :raises TypeError: If service_cls does not inherit from BaseGattService
      :raises ValueError: If UUID conflicts with existing registration and override=False



   .. py:method:: unregister_service_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> None
      :classmethod:


      Unregister a custom service class.

      :param uuid: The service UUID to unregister



   .. py:method:: get_service_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> type[src.bluetooth_sig.gatt.services.base.BaseGattService] | None
      :classmethod:


      Get the service class for a given UUID.

      :param uuid: The service UUID

      :returns: Service class if found, None otherwise

      :raises ValueError: If uuid format is invalid



   .. py:method:: get_service_class_by_name(name: str | src.bluetooth_sig.types.gatt_enums.ServiceName) -> type[src.bluetooth_sig.gatt.services.base.BaseGattService] | None
      :classmethod:


      Get the service class for a given name or enum.



   .. py:method:: get_service_class_by_uuid(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> type[src.bluetooth_sig.gatt.services.base.BaseGattService] | None
      :classmethod:


      Get the service class for a given UUID (alias for get_service_class).



   .. py:method:: create_service(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int, characteristics: src.bluetooth_sig.types.gatt_services.ServiceDiscoveryData) -> src.bluetooth_sig.gatt.services.base.BaseGattService | None
      :classmethod:


      Create a service instance for the given UUID and characteristics.

      :param uuid: Service UUID
      :param characteristics: Dict mapping characteristic UUIDs to CharacteristicInfo

      :returns: Service instance if found, None otherwise

      :raises ValueError: If uuid format is invalid



   .. py:method:: get_all_services() -> list[type[src.bluetooth_sig.gatt.services.base.BaseGattService]]
      :classmethod:


      Get all registered service classes.

      :returns: List of all registered service classes



   .. py:method:: supported_services() -> list[str]
      :classmethod:


      Get a list of supported service UUIDs.



   .. py:method:: supported_service_names() -> list[str]
      :classmethod:


      Get a list of supported service names.



   .. py:method:: clear_custom_registrations() -> None
      :classmethod:


      Clear all custom service registrations (for testing).



.. py:data:: members_registry
   :value: None


.. py:class:: CharacteristicInfo

   Bases: :py:obj:`src.bluetooth_sig.types.base_types.SIGInfo`


   Information about a Bluetooth characteristic from SIG/YAML specifications.

   This contains only static metadata resolved from YAML or SIG specs.
   Runtime properties (read/write/notify capabilities) are stored separately
   on the BaseCharacteristic instance as they're discovered from the actual device.


   .. py:attribute:: value_type
      :type:  src.bluetooth_sig.types.gatt_enums.ValueType


   .. py:attribute:: unit
      :type:  str
      :value: ''



.. py:class:: ServiceInfo

   Bases: :py:obj:`src.bluetooth_sig.types.base_types.SIGInfo`


   Information about a Bluetooth service.


   .. py:attribute:: characteristics
      :type:  list[CharacteristicInfo]


.. py:class:: SIGInfo

   Bases: :py:obj:`msgspec.Struct`


   Base information about Bluetooth SIG characteristics or services.


   .. py:attribute:: uuid
      :type:  src.bluetooth_sig.types.uuid.BluetoothUUID


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: id
      :type:  str
      :value: ''



.. py:class:: ValidationResult

   Bases: :py:obj:`msgspec.Struct`


   Result of characteristic data validation.

   Provides diagnostic information about whether characteristic data
   matches the expected format per Bluetooth SIG specifications.

   This is a lightweight validation result, NOT SIG registry metadata.
   For characteristic metadata (uuid, name, description), query the
   characteristic's info directly.

   .. attribute:: is_valid

      Whether the data format is valid per SIG specs

   .. attribute:: actual_length

      Number of bytes in the data

   .. attribute:: expected_length

      Expected bytes for fixed-length characteristics, None for variable

   .. attribute:: error_message

      Description of validation failure, empty string if valid


   .. py:attribute:: is_valid
      :type:  bool


   .. py:attribute:: actual_length
      :type:  int


   .. py:attribute:: expected_length
      :type:  int | None
      :value: None



   .. py:attribute:: error_message
      :type:  str
      :value: ''



