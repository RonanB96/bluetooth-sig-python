src.bluetooth_sig.gatt
======================

.. py:module:: src.bluetooth_sig.gatt

.. autoapi-nested-parse::

   GATT package initialization.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /reference/api/src/bluetooth_sig/gatt/characteristics/index
   /reference/api/src/bluetooth_sig/gatt/constants/index
   /reference/api/src/bluetooth_sig/gatt/context/index
   /reference/api/src/bluetooth_sig/gatt/descriptor_utils/index
   /reference/api/src/bluetooth_sig/gatt/descriptors/index
   /reference/api/src/bluetooth_sig/gatt/exceptions/index
   /reference/api/src/bluetooth_sig/gatt/registry_utils/index
   /reference/api/src/bluetooth_sig/gatt/resolver/index
   /reference/api/src/bluetooth_sig/gatt/services/index
   /reference/api/src/bluetooth_sig/gatt/uuid_registry/index
   /reference/api/src/bluetooth_sig/gatt/validation/index


Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.ABSOLUTE_ZERO_CELSIUS
   src.bluetooth_sig.gatt.PERCENTAGE_MAX
   src.bluetooth_sig.gatt.SINT8_MAX
   src.bluetooth_sig.gatt.SINT8_MIN
   src.bluetooth_sig.gatt.SINT16_MAX
   src.bluetooth_sig.gatt.TEMPERATURE_RESOLUTION
   src.bluetooth_sig.gatt.UINT8_MAX
   src.bluetooth_sig.gatt.UINT16_MAX
   src.bluetooth_sig.gatt.uuid_registry


Exceptions
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.BluetoothSIGError
   src.bluetooth_sig.gatt.CharacteristicError
   src.bluetooth_sig.gatt.DataParsingError
   src.bluetooth_sig.gatt.ServiceError
   src.bluetooth_sig.gatt.UUIDResolutionError
   src.bluetooth_sig.gatt.ValueRangeError


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.BaseCharacteristic
   src.bluetooth_sig.gatt.BaseGattService
   src.bluetooth_sig.gatt.CharacteristicSpec
   src.bluetooth_sig.gatt.FieldInfo
   src.bluetooth_sig.gatt.UnitMetadata
   src.bluetooth_sig.gatt.UuidRegistry


Package Contents
----------------

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



.. py:data:: ABSOLUTE_ZERO_CELSIUS
   :value: -273.15


.. py:data:: PERCENTAGE_MAX
   :value: 100


.. py:data:: SINT8_MAX
   :value: 127


.. py:data:: SINT8_MIN
   :value: -128


.. py:data:: SINT16_MAX
   :value: 32767


.. py:data:: TEMPERATURE_RESOLUTION
   :value: 0.01


.. py:data:: UINT8_MAX
   :value: 255


.. py:data:: UINT16_MAX
   :value: 65535


.. py:exception:: BluetoothSIGError

   Bases: :py:obj:`Exception`


   Base exception for all Bluetooth SIG related errors.


.. py:exception:: CharacteristicError

   Bases: :py:obj:`BluetoothSIGError`


   Base exception for characteristic-related errors.


.. py:exception:: DataParsingError(characteristic: str, data: bytes | bytearray, reason: str)

   Bases: :py:obj:`CharacteristicError`


   Exception raised when characteristic data parsing fails.


   .. py:attribute:: characteristic


   .. py:attribute:: data


   .. py:attribute:: reason


.. py:exception:: ServiceError

   Bases: :py:obj:`BluetoothSIGError`


   Base exception for service-related errors.


.. py:exception:: UUIDResolutionError(name: str, attempted_names: list[str] | None = None)

   Bases: :py:obj:`BluetoothSIGError`


   Exception raised when UUID resolution fails.


   .. py:attribute:: name


   .. py:attribute:: attempted_names
      :value: []



.. py:exception:: ValueRangeError(field: str, value: Any, min_val: Any, max_val: Any)

   Bases: :py:obj:`DataValidationError`


   Exception raised when a value is outside the expected range.


   .. py:attribute:: min_val


   .. py:attribute:: max_val


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



.. py:class:: CharacteristicSpec

   Bases: :py:obj:`msgspec.Struct`


   Characteristic specification from cross-file YAML references.


   .. py:attribute:: uuid
      :type:  bluetooth_sig.types.uuid.BluetoothUUID


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: field_info
      :type:  FieldInfo


   .. py:attribute:: unit_info
      :type:  UnitMetadata


   .. py:attribute:: description
      :type:  str | None
      :value: None



   .. py:property:: data_type
      :type: str | None


      Get data type from field info.


   .. py:property:: field_size
      :type: str | None


      Get field size from field info.


   .. py:property:: unit_id
      :type: str | None


      Get unit ID from unit info.


   .. py:property:: unit_symbol
      :type: str | None


      Get unit symbol from unit info.


   .. py:property:: base_unit
      :type: str | None


      Get base unit from unit info.


   .. py:property:: resolution_text
      :type: str | None


      Get resolution text from unit info.


.. py:class:: FieldInfo

   Bases: :py:obj:`msgspec.Struct`


   Field-related metadata from YAML.


   .. py:attribute:: name
      :type:  str | None
      :value: None



   .. py:attribute:: data_type
      :type:  str | None
      :value: None



   .. py:attribute:: field_size
      :type:  str | None
      :value: None



   .. py:attribute:: description
      :type:  str | None
      :value: None



.. py:class:: UnitMetadata

   Bases: :py:obj:`msgspec.Struct`


   Unit-related metadata from characteristic YAML specifications.

   This is embedded metadata within characteristic specs, distinct from
   the Units registry which uses UUID-based entries.


   .. py:attribute:: unit_id
      :type:  str | None
      :value: None



   .. py:attribute:: unit_symbol
      :type:  str | None
      :value: None



   .. py:attribute:: base_unit
      :type:  str | None
      :value: None



   .. py:attribute:: resolution_text
      :type:  str | None
      :value: None



.. py:class:: UuidRegistry

   Registry for Bluetooth SIG UUIDs with canonical storage + alias indices.

   This registry stores a number of internal caches and mappings which
   legitimately exceed the default pylint instance attribute limit. The
   complexity is intentional and centralised; an inline disable is used to
   avoid noisy global configuration changes.


   .. py:method:: register_characteristic(uuid: bluetooth_sig.types.uuid.BluetoothUUID, name: str, identifier: str | None = None, unit: str | None = None, value_type: bluetooth_sig.types.gatt_enums.ValueType | None = None, override: bool = False) -> None

      Register a custom characteristic at runtime.

      :param uuid: The Bluetooth UUID for the characteristic
      :param name: Human-readable name
      :param identifier: Optional identifier (auto-generated if not provided)
      :param unit: Optional unit of measurement
      :param value_type: Optional value type
      :param override: If True, allow overriding existing entries



   .. py:method:: register_service(uuid: bluetooth_sig.types.uuid.BluetoothUUID, name: str, identifier: str | None = None, override: bool = False) -> None

      Register a custom service at runtime.

      :param uuid: The Bluetooth UUID for the service
      :param name: Human-readable name
      :param identifier: Optional identifier (auto-generated if not provided)
      :param override: If True, allow overriding existing entries



   .. py:method:: get_service_info(key: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bluetooth_sig.types.ServiceInfo | None

      Get information about a service by UUID, name, or ID.



   .. py:method:: get_characteristic_info(identifier: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bluetooth_sig.types.CharacteristicInfo | None

      Get information about a characteristic by UUID, name, or ID.



   .. py:method:: get_descriptor_info(identifier: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bluetooth_sig.types.registry.descriptor_types.DescriptorInfo | None

      Get information about a descriptor by UUID, name, or ID.



   .. py:method:: resolve_characteristic_spec(characteristic_name: str) -> src.bluetooth_sig.types.registry.CharacteristicSpec | None

      Resolve characteristic specification with rich YAML metadata.

      This method provides detailed characteristic information including data types,
      field sizes, units, and descriptions by cross-referencing multiple YAML sources.

      :param characteristic_name: Name of the characteristic (e.g., "Temperature", "Battery Level")

      :returns: CharacteristicSpec with full metadata, or None if not found

      .. admonition:: Example

         spec = uuid_registry.resolve_characteristic_spec("Temperature")
         if spec:
             print(f"UUID: {spec.uuid}, Unit: {spec.unit_symbol}, Type: {spec.data_type}")



   .. py:method:: get_signed_from_data_type(data_type: str | None) -> bool

      Determine if data type is signed from GSS data type.

      :param data_type: GSS data type string (e.g., "sint16", "float32", "uint8")

      :returns: True if the type represents signed values, False otherwise



   .. py:method:: get_byte_order_hint() -> str
      :staticmethod:


      Get byte order hint for Bluetooth SIG specifications.

      :returns: "little" - Bluetooth SIG uses little-endian by convention



   .. py:method:: clear_custom_registrations() -> None

      Clear all custom registrations (for testing).



.. py:data:: uuid_registry

