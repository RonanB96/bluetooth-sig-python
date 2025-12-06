src.bluetooth_sig.gatt.characteristics.base
===========================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.base

.. autoapi-nested-parse::

   Base class for GATT characteristics.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic
   src.bluetooth_sig.gatt.characteristics.base.CharacteristicData
   src.bluetooth_sig.gatt.characteristics.base.CharacteristicMeta
   src.bluetooth_sig.gatt.characteristics.base.SIGCharacteristicResolver
   src.bluetooth_sig.gatt.characteristics.base.ValidationConfig


Module Contents
---------------

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

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: add_descriptor(descriptor: src.bluetooth_sig.gatt.descriptors.BaseDescriptor) -> None

      Add a descriptor to this characteristic.

      :param descriptor: The descriptor instance to add



   .. py:method:: build_value(data: Any) -> bytearray

      Build characteristic bytes from value with validation.

      High-level encoding method that validates before encoding, mirroring
      how parse_value() validates after decode_value().

      :param data: Value to encode (type depends on characteristic)

      :returns: Validated and encoded bytes for characteristic write

      :raises ValueError: If data fails validation
      :raises TypeError: If data type is incorrect
      :raises NotImplementedError: If characteristic doesn't support encoding



   .. py:method:: can_notify() -> bool

      Check if this characteristic supports notifications.

      :returns: True if the characteristic has a CCCD descriptor, False otherwise



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> Any

      Parse the characteristic's raw value.

      If _template is set, uses the template's decode_value method.
      Otherwise, subclasses must override this method.

      :param data: Raw bytes from the characteristic read
      :param ctx: Optional context information for parsing

      :returns: Parsed value in the appropriate type

      :raises NotImplementedError: If no template is set and subclass doesn't override



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



   .. py:method:: enhance_error_message_with_descriptors(base_message: str, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> str

      Enhance error message with descriptor information for better debugging.

      :param base_message: Original error message
      :param ctx: Characteristic context containing descriptors

      :returns: Enhanced error message with descriptor context



   .. py:method:: get_allows_sig_override() -> bool
      :classmethod:


      Check if this characteristic class allows overriding SIG characteristics.

      Custom characteristics that need to override official Bluetooth SIG
      characteristics must set _allows_sig_override = True as a class attribute.

      :returns: True if SIG override is allowed, False otherwise.



   .. py:method:: get_byte_order_hint() -> str

      Get byte order hint (Bluetooth SIG uses little-endian by convention).



   .. py:method:: get_cccd() -> src.bluetooth_sig.gatt.descriptors.BaseDescriptor | None

      Get the Client Characteristic Configuration Descriptor (CCCD).

      :returns: CCCD descriptor instance if present, None otherwise



   .. py:method:: get_class_uuid() -> src.bluetooth_sig.types.uuid.BluetoothUUID | None
      :classmethod:


      Get the characteristic UUID for this class without creating an instance.

      This is the public API for registry and other modules to resolve UUIDs.

      :returns: BluetoothUUID if the class has a resolvable UUID, None otherwise.



   .. py:method:: get_configured_info() -> src.bluetooth_sig.types.CharacteristicInfo | None
      :classmethod:


      Get the class-level configured CharacteristicInfo.

      This provides public access to the _configured_info attribute that is set
      by __init_subclass__ for custom characteristics.

      :returns: CharacteristicInfo if configured, None otherwise



   .. py:method:: get_context_characteristic(ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None, characteristic_name: src.bluetooth_sig.types.gatt_enums.CharacteristicName | str | type[BaseCharacteristic]) -> src.bluetooth_sig.types.CharacteristicDataProtocol | None

      Find a characteristic in a context by name or class.

      :param ctx: Context containing other characteristics.
      :param characteristic_name: Enum, string name, or characteristic class.

      :returns: Characteristic data if found, None otherwise.



   .. py:method:: get_descriptor(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID) -> src.bluetooth_sig.gatt.descriptors.BaseDescriptor | None

      Get a descriptor by UUID.

      :param uuid: Descriptor UUID (string or BluetoothUUID)

      :returns: Descriptor instance if found, None otherwise



   .. py:method:: get_descriptor_from_context(ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None, descriptor_class: type[src.bluetooth_sig.gatt.descriptors.BaseDescriptor]) -> src.bluetooth_sig.types.registry.descriptor_types.DescriptorData | None

      Get a descriptor of the specified type from the context.

      :param ctx: Characteristic context containing descriptors
      :param descriptor_class: The descriptor class to look for (e.g., ValidRangeDescriptor)

      :returns: DescriptorData if found, None otherwise



   .. py:method:: get_descriptors() -> dict[str, src.bluetooth_sig.gatt.descriptors.BaseDescriptor]

      Get all descriptors for this characteristic.

      :returns: Dict mapping descriptor UUID strings to descriptor instances



   .. py:method:: get_presentation_format_from_context(ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> src.bluetooth_sig.gatt.descriptors.characteristic_presentation_format.CharacteristicPresentationFormatData | None

      Get presentation format from descriptor context if available.

      :param ctx: Characteristic context containing descriptors

      :returns: CharacteristicPresentationFormatData if present, None otherwise



   .. py:method:: get_user_description_from_context(ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> str | None

      Get user description from descriptor context if available.

      :param ctx: Characteristic context containing descriptors

      :returns: User description string if present, None otherwise



   .. py:method:: get_valid_range_from_context(ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> tuple[int | float, int | float] | None

      Get valid range from descriptor context if available.

      :param ctx: Characteristic context containing descriptors

      :returns: Tuple of (min, max) values if Valid Range descriptor present, None otherwise



   .. py:method:: get_yaml_data_type() -> str | None

      Get the data type from YAML automation (e.g., 'sint16', 'uint8').



   .. py:method:: get_yaml_field_size() -> int | None

      Get the field size in bytes from YAML automation.



   .. py:method:: get_yaml_resolution_text() -> str | None

      Get the resolution description text from YAML automation.



   .. py:method:: get_yaml_unit_id() -> str | None

      Get the Bluetooth SIG unit identifier from YAML automation.



   .. py:method:: is_signed_from_yaml() -> bool

      Determine if the data type is signed based on YAML automation.



   .. py:method:: matches_uuid(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID) -> bool
      :classmethod:


      Check if this characteristic matches the given UUID.



   .. py:method:: parse_value(data: bytes | bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> CharacteristicData

      Parse raw characteristic data into structured value with validation.

      :param data: Raw bytes from the characteristic read
      :param ctx: Optional context with device info and other characteristics

      :returns: CharacteristicData with parsed value (stored in self.last_parsed)



   .. py:method:: validate_value_against_descriptor_range(value: int | float, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> bool

      Validate a value against descriptor-defined valid range.

      :param value: Value to validate
      :param ctx: Characteristic context containing descriptors

      :returns: True if value is within valid range or no range defined, False otherwise



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: False



   .. py:property:: description
      :type: str


      Get the characteristic description from GSS specification.


   .. py:property:: display_name
      :type: str


      Get the display name for this characteristic.

      Uses explicit _characteristic_name if set, otherwise falls back
      to class name.


   .. py:attribute:: expected_length
      :type:  int | None
      :value: None



   .. py:attribute:: expected_type
      :type:  type | None
      :value: None



   .. py:property:: info
      :type: src.bluetooth_sig.types.CharacteristicInfo


      Characteristic information.


   .. py:attribute:: last_parsed
      :type:  CharacteristicData | None
      :value: None



   .. py:attribute:: max_length
      :type:  int | None
      :value: None



   .. py:attribute:: max_value
      :type:  int | float | None
      :value: None



   .. py:attribute:: min_length
      :type:  int | None
      :value: None



   .. py:attribute:: min_value
      :type:  int | float | None
      :value: None



   .. py:property:: name
      :type: str


      Get the characteristic name from _info.


   .. py:property:: optional_dependencies
      :type: list[str]


      Get resolved optional dependency UUID strings.


   .. py:attribute:: properties
      :type:  list[src.bluetooth_sig.types.gatt_enums.GattProperty]
      :value: None



   .. py:property:: required_dependencies
      :type: list[str]


      Get resolved required dependency UUID strings.


   .. py:property:: size
      :type: int | None


      Get the size in bytes for this characteristic from YAML specifications.

      Returns the field size from YAML automation if available, otherwise None.
      This is useful for determining the expected data length for parsing
      and encoding.


   .. py:property:: spec
      :type: src.bluetooth_sig.gatt.uuid_registry.CharacteristicSpec | None


      Get the full GSS specification with description and detailed metadata.


   .. py:property:: unit
      :type: str


      Get the unit of measurement from _info.

      Returns empty string for characteristics without units (e.g., bitfields).


   .. py:property:: uuid
      :type: src.bluetooth_sig.types.uuid.BluetoothUUID


      Get the characteristic UUID from _info.


   .. py:attribute:: value_type
      :type:  src.bluetooth_sig.types.gatt_enums.ValueType


   .. py:property:: value_type_resolved
      :type: src.bluetooth_sig.types.gatt_enums.ValueType


      Get the value type from _info.


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


   .. py:attribute:: error_message
      :type:  str
      :value: ''



   .. py:attribute:: field_errors
      :type:  list[src.bluetooth_sig.types.ParseFieldError]


   .. py:property:: info
      :type: src.bluetooth_sig.types.CharacteristicInfo


      Characteristic metadata.


   .. py:property:: name
      :type: str


      Characteristic name.


   .. py:attribute:: parse_success
      :type:  bool
      :value: False



   .. py:attribute:: parse_trace
      :type:  list[str]


   .. py:property:: properties
      :type: list[src.bluetooth_sig.types.gatt_enums.GattProperty]


      BLE GATT properties.


   .. py:attribute:: raw_data
      :type:  bytes
      :value: b''



   .. py:property:: unit
      :type: str


      Unit of measurement.


   .. py:property:: uuid
      :type: src.bluetooth_sig.types.uuid.BluetoothUUID


      Characteristic UUID.


   .. py:attribute:: value
      :type:  Any | None
      :value: None



.. py:class:: CharacteristicMeta

   Bases: :py:obj:`abc.ABCMeta`


   Metaclass to automatically handle template flags for characteristics.

   Create the characteristic class and handle template markers.

   This metaclass hook ensures template classes and concrete
   implementations are correctly annotated with the ``_is_template``
   attribute before the class object is created.


.. py:class:: SIGCharacteristicResolver

   Resolves SIG characteristic information from YAML and registry.

   This class handles all SIG characteristic resolution logic, separating
   concerns from the BaseCharacteristic constructor. Uses shared utilities
   from the resolver module to avoid code duplication.


   .. py:method:: resolve_for_class(char_class: type[BaseCharacteristic]) -> src.bluetooth_sig.types.CharacteristicInfo
      :staticmethod:


      Resolve CharacteristicInfo for a SIG characteristic class.

      :param char_class: The characteristic class to resolve info for

      :returns: CharacteristicInfo with resolved UUID, name, value_type, unit

      :raises UUIDResolutionError: If no UUID can be resolved for the class



   .. py:method:: resolve_from_registry(char_class: type[BaseCharacteristic]) -> src.bluetooth_sig.types.CharacteristicInfo | None
      :staticmethod:


      Fallback to registry resolution using shared search strategy.



   .. py:method:: resolve_yaml_spec_for_class(char_class: type[BaseCharacteristic]) -> src.bluetooth_sig.gatt.uuid_registry.CharacteristicSpec | None
      :staticmethod:


      Resolve YAML spec for a characteristic class using shared name variant logic.



   .. py:attribute:: camel_case_to_display_name


.. py:class:: ValidationConfig

   Bases: :py:obj:`msgspec.Struct`


   Configuration for characteristic validation constraints.

   Groups validation parameters into a single, optional configuration object
   to simplify BaseCharacteristic constructor signatures.


   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: False



   .. py:attribute:: expected_length
      :type:  int | None
      :value: None



   .. py:attribute:: expected_type
      :type:  type | None
      :value: None



   .. py:attribute:: max_length
      :type:  int | None
      :value: None



   .. py:attribute:: max_value
      :type:  int | float | None
      :value: None



   .. py:attribute:: min_length
      :type:  int | None
      :value: None



   .. py:attribute:: min_value
      :type:  int | float | None
      :value: None



