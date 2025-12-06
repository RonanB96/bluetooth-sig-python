src.bluetooth_sig.gatt.exceptions
=================================

.. py:module:: src.bluetooth_sig.gatt.exceptions

.. autoapi-nested-parse::

   GATT exceptions for the Bluetooth SIG library.



Exceptions
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.exceptions.BluetoothSIGError
   src.bluetooth_sig.gatt.exceptions.CharacteristicError
   src.bluetooth_sig.gatt.exceptions.DataEncodingError
   src.bluetooth_sig.gatt.exceptions.DataParsingError
   src.bluetooth_sig.gatt.exceptions.DataValidationError
   src.bluetooth_sig.gatt.exceptions.EnumValueError
   src.bluetooth_sig.gatt.exceptions.IEEE11073Error
   src.bluetooth_sig.gatt.exceptions.InsufficientDataError
   src.bluetooth_sig.gatt.exceptions.MissingDependencyError
   src.bluetooth_sig.gatt.exceptions.ParseFieldError
   src.bluetooth_sig.gatt.exceptions.ServiceCharacteristicMismatchError
   src.bluetooth_sig.gatt.exceptions.ServiceError
   src.bluetooth_sig.gatt.exceptions.TemplateConfigurationError
   src.bluetooth_sig.gatt.exceptions.TypeMismatchError
   src.bluetooth_sig.gatt.exceptions.UUIDCollisionError
   src.bluetooth_sig.gatt.exceptions.UUIDRequiredError
   src.bluetooth_sig.gatt.exceptions.UUIDResolutionError
   src.bluetooth_sig.gatt.exceptions.ValueRangeError
   src.bluetooth_sig.gatt.exceptions.YAMLResolutionError


Module Contents
---------------

.. py:exception:: BluetoothSIGError

   Bases: :py:obj:`Exception`


   Base exception for all Bluetooth SIG related errors.

   Initialize self.  See help(type(self)) for accurate signature.


.. py:exception:: CharacteristicError

   Bases: :py:obj:`BluetoothSIGError`


   Base exception for characteristic-related errors.

   Initialize self.  See help(type(self)) for accurate signature.


.. py:exception:: DataEncodingError(characteristic: str, value: Any, reason: str)

   Bases: :py:obj:`CharacteristicError`


   Exception raised when characteristic data encoding fails.

   Initialise DataEncodingError.

   :param characteristic: The characteristic name.
   :param value: The value that failed to encode.
   :param reason: Reason for the encoding failure.


   .. py:attribute:: characteristic


   .. py:attribute:: reason


   .. py:attribute:: value


.. py:exception:: DataParsingError(characteristic: str, data: bytes | bytearray, reason: str)

   Bases: :py:obj:`CharacteristicError`


   Exception raised when characteristic data parsing fails.

   Initialise DataParsingError.

   :param characteristic: The characteristic name.
   :param data: The raw data that failed to parse.
   :param reason: Reason for the parsing failure.


   .. py:attribute:: characteristic


   .. py:attribute:: data


   .. py:attribute:: reason


.. py:exception:: DataValidationError(field: str, value: Any, expected: str)

   Bases: :py:obj:`CharacteristicError`


   Exception raised when characteristic data validation fails.

   Initialise DataValidationError.

   :param field: The field name.
   :param value: The value that failed validation.
   :param expected: Expected value or description.


   .. py:attribute:: expected


   .. py:attribute:: field


   .. py:attribute:: value


.. py:exception:: EnumValueError(field: str, value: Any, enum_class: type, valid_values: list[Any])

   Bases: :py:obj:`DataValidationError`


   Exception raised when an enum value is invalid.

   Initialise EnumValidationError.

   :param field: The field name.
   :param value: The value to validate.
   :param enum_class: Enum class for validation.
   :param valid_values: List of valid values.


   .. py:attribute:: enum_class


   .. py:attribute:: valid_values


.. py:exception:: IEEE11073Error(data: bytes | bytearray, format_type: str, reason: str)

   Bases: :py:obj:`DataParsingError`


   Exception raised when IEEE 11073 format parsing fails.

   Initialise DataFormatError.

   :param data: The raw data.
   :param format_type: Format type expected.
   :param reason: Reason for the format error.


   .. py:attribute:: format_type


.. py:exception:: InsufficientDataError(characteristic: str, data: bytes | bytearray, required: int)

   Bases: :py:obj:`DataParsingError`


   Exception raised when there is insufficient data for parsing.

   Initialise InsufficientDataError.

   :param characteristic: The characteristic name.
   :param data: The raw data.
   :param required: Required length of data.


   .. py:attribute:: actual


   .. py:attribute:: required


.. py:exception:: MissingDependencyError(characteristic: str, missing_dependencies: list[str])

   Bases: :py:obj:`CharacteristicError`


   Exception raised when a required dependency is missing for multi-characteristic parsing.

   Initialise DependencyValidationError.

   :param characteristic: The characteristic name.
   :param missing_dependencies: List of missing dependencies.


   .. py:attribute:: characteristic


   .. py:attribute:: missing_dependencies


.. py:exception:: ParseFieldError(characteristic: str, field: str, data: bytes | bytearray, reason: str, offset: int | None = None)

   Bases: :py:obj:`DataParsingError`


   Exception raised when a specific field fails to parse.

   This exception provides detailed context about which field failed, where it
   failed in the data, and why it failed. This enables actionable error messages
   and structured error reporting.

   NOTE: This exception intentionally has more arguments than the standard limit
   to provide complete field-level diagnostic information. The additional parameters
   (field, offset) are essential for actionable error messages and field-level debugging.

   .. attribute:: field

      Name of the field that failed (e.g., "temperature", "flags")

   .. attribute:: offset

      Byte offset where the field starts in the raw data

   .. attribute:: expected

      Description of what was expected

   .. attribute:: actual

      Description of what was actually encountered

   Initialise ParseFieldError.

   :param characteristic: The characteristic name.
   :param field: The field name.
   :param data: The raw data.
   :param reason: Reason for the parsing failure.
   :param offset: Optional offset in the data.


   .. py:attribute:: field


   .. py:attribute:: field_reason


   .. py:attribute:: offset
      :value: None



.. py:exception:: ServiceCharacteristicMismatchError(service: str, missing_characteristics: list[str])

   Bases: :py:obj:`ServiceError`


   Exception raised when expected characteristics are not found in a service.

   service.

   Initialise ExpectedCharacteristicNotFound.

   :param service: The service name.
   :param missing_characteristics: List of missing characteristics.


   .. py:attribute:: missing_characteristics


   .. py:attribute:: service


.. py:exception:: ServiceError

   Bases: :py:obj:`BluetoothSIGError`


   Base exception for service-related errors.

   Initialize self.  See help(type(self)) for accurate signature.


.. py:exception:: TemplateConfigurationError(template: str, configuration_issue: str)

   Bases: :py:obj:`CharacteristicError`


   Exception raised when a template is incorrectly configured.

   Initialise TemplateConfigurationError.

   :param template: The template name.
   :param configuration_issue: Description of the configuration issue.


   .. py:attribute:: configuration_issue


   .. py:attribute:: template


.. py:exception:: TypeMismatchError(field: str, value: Any, expected_type: type | tuple[type, Ellipsis])

   Bases: :py:obj:`DataValidationError`


   Exception raised when a value has an unexpected type.

   Initialise TypeValidationError.

   :param field: The field name.
   :param value: The value to validate.
   :param expected_type: Expected type(s).


   .. py:attribute:: actual_type
      :type:  type


   .. py:attribute:: expected_type
      :type:  type | tuple[type, Ellipsis]


.. py:exception:: UUIDCollisionError(uuid: src.bluetooth_sig.types.uuid.BluetoothUUID | str, existing_name: str, class_name: str)

   Bases: :py:obj:`BluetoothSIGError`


   Exception raised when attempting to use a UUID that already exists in SIG registry.

   Initialise UUIDRegistrationError.

   :param uuid: The UUID value.
   :param existing_name: Existing name for the UUID.
   :param class_name: Name of the class.


   .. py:attribute:: class_name


   .. py:attribute:: existing_name


   .. py:attribute:: uuid


.. py:exception:: UUIDRequiredError(class_name: str, entity_type: str)

   Bases: :py:obj:`BluetoothSIGError`


   Exception raised when a UUID is required but not provided or invalid.

   Initialise EntityRegistrationError.

   :param class_name: Name of the class.
   :param entity_type: Type of the entity.


   .. py:attribute:: class_name


   .. py:attribute:: entity_type


.. py:exception:: UUIDResolutionError(name: str, attempted_names: list[str] | None = None)

   Bases: :py:obj:`BluetoothSIGError`


   Exception raised when UUID resolution fails.

   Initialise UUIDResolutionError.

   :param name: The name for which UUID resolution failed.
   :param attempted_names: List of attempted names.


   .. py:attribute:: attempted_names
      :value: []



   .. py:attribute:: name


.. py:exception:: ValueRangeError(field: str, value: Any, min_val: Any, max_val: Any)

   Bases: :py:obj:`DataValidationError`


   Exception raised when a value is outside the expected range.

   Initialise RangeValidationError.

   :param field: The field name.
   :param value: The value to validate.
   :param min_val: Minimum valid value.
   :param max_val: Maximum valid value.


   .. py:attribute:: max_val


   .. py:attribute:: min_val


.. py:exception:: YAMLResolutionError(name: str, yaml_type: str)

   Bases: :py:obj:`BluetoothSIGError`


   Exception raised when YAML specification resolution fails.

   Initialise YAMLSchemaError.

   :param name: Name of the YAML entity.
   :param yaml_type: Type of the YAML entity.


   .. py:attribute:: name


   .. py:attribute:: yaml_type


