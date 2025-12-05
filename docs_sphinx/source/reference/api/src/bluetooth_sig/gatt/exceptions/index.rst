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
   src.bluetooth_sig.gatt.exceptions.ServiceError
   src.bluetooth_sig.gatt.exceptions.UUIDResolutionError
   src.bluetooth_sig.gatt.exceptions.DataParsingError
   src.bluetooth_sig.gatt.exceptions.ParseFieldError
   src.bluetooth_sig.gatt.exceptions.DataEncodingError
   src.bluetooth_sig.gatt.exceptions.DataValidationError
   src.bluetooth_sig.gatt.exceptions.InsufficientDataError
   src.bluetooth_sig.gatt.exceptions.ValueRangeError
   src.bluetooth_sig.gatt.exceptions.TypeMismatchError
   src.bluetooth_sig.gatt.exceptions.MissingDependencyError
   src.bluetooth_sig.gatt.exceptions.EnumValueError
   src.bluetooth_sig.gatt.exceptions.IEEE11073Error
   src.bluetooth_sig.gatt.exceptions.YAMLResolutionError
   src.bluetooth_sig.gatt.exceptions.ServiceCharacteristicMismatchError
   src.bluetooth_sig.gatt.exceptions.TemplateConfigurationError
   src.bluetooth_sig.gatt.exceptions.UUIDRequiredError
   src.bluetooth_sig.gatt.exceptions.UUIDCollisionError


Module Contents
---------------

.. py:exception:: BluetoothSIGError

   Bases: :py:obj:`Exception`


   Base exception for all Bluetooth SIG related errors.


.. py:exception:: CharacteristicError

   Bases: :py:obj:`BluetoothSIGError`


   Base exception for characteristic-related errors.


.. py:exception:: ServiceError

   Bases: :py:obj:`BluetoothSIGError`


   Base exception for service-related errors.


.. py:exception:: UUIDResolutionError(name: str, attempted_names: list[str] | None = None)

   Bases: :py:obj:`BluetoothSIGError`


   Exception raised when UUID resolution fails.


   .. py:attribute:: name


   .. py:attribute:: attempted_names
      :value: []



.. py:exception:: DataParsingError(characteristic: str, data: bytes | bytearray, reason: str)

   Bases: :py:obj:`CharacteristicError`


   Exception raised when characteristic data parsing fails.


   .. py:attribute:: characteristic


   .. py:attribute:: data


   .. py:attribute:: reason


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


   .. py:attribute:: field


   .. py:attribute:: offset
      :value: None



   .. py:attribute:: field_reason


.. py:exception:: DataEncodingError(characteristic: str, value: Any, reason: str)

   Bases: :py:obj:`CharacteristicError`


   Exception raised when characteristic data encoding fails.


   .. py:attribute:: characteristic


   .. py:attribute:: value


   .. py:attribute:: reason


.. py:exception:: DataValidationError(field: str, value: Any, expected: str)

   Bases: :py:obj:`CharacteristicError`


   Exception raised when characteristic data validation fails.


   .. py:attribute:: field


   .. py:attribute:: value


   .. py:attribute:: expected


.. py:exception:: InsufficientDataError(characteristic: str, data: bytes | bytearray, required: int)

   Bases: :py:obj:`DataParsingError`


   Exception raised when there is insufficient data for parsing.


   .. py:attribute:: required


   .. py:attribute:: actual


.. py:exception:: ValueRangeError(field: str, value: Any, min_val: Any, max_val: Any)

   Bases: :py:obj:`DataValidationError`


   Exception raised when a value is outside the expected range.


   .. py:attribute:: min_val


   .. py:attribute:: max_val


.. py:exception:: TypeMismatchError(field: str, value: Any, expected_type: type | tuple[type, Ellipsis])

   Bases: :py:obj:`DataValidationError`


   Exception raised when a value has an unexpected type.


   .. py:attribute:: expected_type
      :type:  type | tuple[type, Ellipsis]


   .. py:attribute:: actual_type
      :type:  type


.. py:exception:: MissingDependencyError(characteristic: str, missing_dependencies: list[str])

   Bases: :py:obj:`CharacteristicError`


   Exception raised when a required dependency is missing for multi-characteristic parsing.


   .. py:attribute:: characteristic


   .. py:attribute:: missing_dependencies


.. py:exception:: EnumValueError(field: str, value: Any, enum_class: type, valid_values: list[Any])

   Bases: :py:obj:`DataValidationError`


   Exception raised when an enum value is invalid.


   .. py:attribute:: enum_class


   .. py:attribute:: valid_values


.. py:exception:: IEEE11073Error(data: bytes | bytearray, format_type: str, reason: str)

   Bases: :py:obj:`DataParsingError`


   Exception raised when IEEE 11073 format parsing fails.


   .. py:attribute:: format_type


.. py:exception:: YAMLResolutionError(name: str, yaml_type: str)

   Bases: :py:obj:`BluetoothSIGError`


   Exception raised when YAML specification resolution fails.


   .. py:attribute:: name


   .. py:attribute:: yaml_type


.. py:exception:: ServiceCharacteristicMismatchError(service: str, missing_characteristics: list[str])

   Bases: :py:obj:`ServiceError`


   Exception raised when expected characteristics are not found in a service.

   service.


   .. py:attribute:: service


   .. py:attribute:: missing_characteristics


.. py:exception:: TemplateConfigurationError(template: str, configuration_issue: str)

   Bases: :py:obj:`CharacteristicError`


   Exception raised when a template is incorrectly configured.


   .. py:attribute:: template


   .. py:attribute:: configuration_issue


.. py:exception:: UUIDRequiredError(class_name: str, entity_type: str)

   Bases: :py:obj:`BluetoothSIGError`


   Exception raised when a UUID is required but not provided or invalid.


   .. py:attribute:: class_name


   .. py:attribute:: entity_type


.. py:exception:: UUIDCollisionError(uuid: src.bluetooth_sig.types.uuid.BluetoothUUID | str, existing_name: str, class_name: str)

   Bases: :py:obj:`BluetoothSIGError`


   Exception raised when attempting to use a UUID that already exists in SIG registry.


   .. py:attribute:: uuid


   .. py:attribute:: existing_name


   .. py:attribute:: class_name


