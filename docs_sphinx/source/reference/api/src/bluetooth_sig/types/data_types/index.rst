src.bluetooth_sig.types.data_types
==================================

.. py:module:: src.bluetooth_sig.types.data_types

.. autoapi-nested-parse::

   Data types for Bluetooth SIG standards.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.data_types.ParseFieldError
   src.bluetooth_sig.types.data_types.DateData
   src.bluetooth_sig.types.data_types.CharacteristicInfo
   src.bluetooth_sig.types.data_types.ServiceInfo
   src.bluetooth_sig.types.data_types.ValidationResult


Module Contents
---------------

.. py:class:: ParseFieldError

   Bases: :py:obj:`msgspec.Struct`


   Represents a field-level parsing error with diagnostic information.

   This provides structured error information similar to Pydantic's validation
   errors, making it easier to debug which specific field failed and why.

   .. attribute:: field

      Name of the field that failed (e.g., "temperature", "flags")

   .. attribute:: reason

      Human-readable description of why parsing failed

   .. attribute:: offset

      Optional byte offset where the field starts in raw data

   .. attribute:: raw_slice

      Optional raw bytes that were being parsed when error occurred


   .. py:attribute:: field
      :type:  str


   .. py:attribute:: reason
      :type:  str


   .. py:attribute:: offset
      :type:  int | None
      :value: None



   .. py:attribute:: raw_slice
      :type:  bytes | None
      :value: None



.. py:class:: DateData

   Bases: :py:obj:`msgspec.Struct`


   Shared data type for date values with year, month, and day fields.


   .. py:attribute:: year
      :type:  int


   .. py:attribute:: month
      :type:  int


   .. py:attribute:: day
      :type:  int


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



