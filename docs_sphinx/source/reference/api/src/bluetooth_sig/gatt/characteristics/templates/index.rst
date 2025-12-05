src.bluetooth_sig.gatt.characteristics.templates
================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.templates

.. autoapi-nested-parse::

   Coding templates for characteristic composition patterns.

   This module provides reusable coding template classes that can be composed into
   characteristics via dependency injection. Templates are pure coding strategies
   that do NOT inherit from BaseCharacteristic.

   All templates follow the CodingTemplate protocol and can be used by both SIG
   and custom characteristics through composition.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.templates.CodingTemplate
   src.bluetooth_sig.gatt.characteristics.templates.VectorData
   src.bluetooth_sig.gatt.characteristics.templates.Vector2DData
   src.bluetooth_sig.gatt.characteristics.templates.TimeData
   src.bluetooth_sig.gatt.characteristics.templates.Uint8Template
   src.bluetooth_sig.gatt.characteristics.templates.Sint8Template
   src.bluetooth_sig.gatt.characteristics.templates.Uint16Template
   src.bluetooth_sig.gatt.characteristics.templates.Sint16Template
   src.bluetooth_sig.gatt.characteristics.templates.Uint32Template
   src.bluetooth_sig.gatt.characteristics.templates.ScaledUint16Template
   src.bluetooth_sig.gatt.characteristics.templates.ScaledSint16Template
   src.bluetooth_sig.gatt.characteristics.templates.ScaledSint8Template
   src.bluetooth_sig.gatt.characteristics.templates.ScaledUint32Template
   src.bluetooth_sig.gatt.characteristics.templates.ScaledUint24Template
   src.bluetooth_sig.gatt.characteristics.templates.ScaledSint24Template
   src.bluetooth_sig.gatt.characteristics.templates.PercentageTemplate
   src.bluetooth_sig.gatt.characteristics.templates.TemperatureTemplate
   src.bluetooth_sig.gatt.characteristics.templates.ConcentrationTemplate
   src.bluetooth_sig.gatt.characteristics.templates.PressureTemplate
   src.bluetooth_sig.gatt.characteristics.templates.TimeDataTemplate
   src.bluetooth_sig.gatt.characteristics.templates.IEEE11073FloatTemplate
   src.bluetooth_sig.gatt.characteristics.templates.Float32Template
   src.bluetooth_sig.gatt.characteristics.templates.Utf8StringTemplate
   src.bluetooth_sig.gatt.characteristics.templates.VectorTemplate
   src.bluetooth_sig.gatt.characteristics.templates.Vector2DTemplate


Module Contents
---------------

.. py:class:: CodingTemplate

   Bases: :py:obj:`abc.ABC`


   Abstract base class for coding templates.

   Templates are pure coding utilities that don't inherit from BaseCharacteristic.
   They provide coding strategies that can be injected into characteristics.
   All templates MUST inherit from this base class and implement the required methods.


   .. py:method:: decode_value(data: bytearray, offset: int = 0, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> Any
      :abstractmethod:


      Decode raw bytes to typed value.

      :param data: Raw bytes to parse
      :param offset: Byte offset to start parsing from
      :param ctx: Optional context for parsing

      :returns: Parsed value of appropriate type (int, float, str, bytes, or custom dataclass)



   .. py:method:: encode_value(value: Any) -> bytearray
      :abstractmethod:


      Encode typed value to raw bytes.

      :param value: Typed value to encode

      :returns: Raw bytes representing the value



   .. py:property:: data_size
      :type: int

      :abstractmethod:


      Size of data in bytes that this template handles.


.. py:class:: VectorData

   Bases: :py:obj:`msgspec.Struct`


   3D vector measurement data.


   .. py:attribute:: x_axis
      :type:  float


   .. py:attribute:: y_axis
      :type:  float


   .. py:attribute:: z_axis
      :type:  float


.. py:class:: Vector2DData

   Bases: :py:obj:`msgspec.Struct`


   2D vector measurement data.


   .. py:attribute:: x_axis
      :type:  float


   .. py:attribute:: y_axis
      :type:  float


.. py:class:: TimeData

   Bases: :py:obj:`msgspec.Struct`


   Time characteristic data structure.


   .. py:attribute:: date_time
      :type:  datetime.datetime | None


   .. py:attribute:: day_of_week
      :type:  src.bluetooth_sig.types.gatt_enums.DayOfWeek


   .. py:attribute:: fractions256
      :type:  int


   .. py:attribute:: adjust_reason
      :type:  src.bluetooth_sig.types.gatt_enums.AdjustReason


.. py:class:: Uint8Template

   Bases: :py:obj:`CodingTemplate`


   Template for 8-bit unsigned integer parsing (0-255).


   .. py:property:: data_size
      :type: int


      1 byte.

      :type: Size


   .. py:method:: decode_value(data: bytearray, offset: int = 0, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> int

      Parse 8-bit unsigned integer.



   .. py:method:: encode_value(value: int) -> bytearray

      Encode uint8 value to bytes.



.. py:class:: Sint8Template

   Bases: :py:obj:`CodingTemplate`


   Template for 8-bit signed integer parsing (-128 to 127).


   .. py:property:: data_size
      :type: int


      1 byte.

      :type: Size


   .. py:method:: decode_value(data: bytearray, offset: int = 0, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> int

      Parse 8-bit signed integer.



   .. py:method:: encode_value(value: int) -> bytearray

      Encode sint8 value to bytes.



.. py:class:: Uint16Template

   Bases: :py:obj:`CodingTemplate`


   Template for 16-bit unsigned integer parsing (0-65535).


   .. py:property:: data_size
      :type: int


      2 bytes.

      :type: Size


   .. py:method:: decode_value(data: bytearray, offset: int = 0, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> int

      Parse 16-bit unsigned integer.



   .. py:method:: encode_value(value: int) -> bytearray

      Encode uint16 value to bytes.



.. py:class:: Sint16Template

   Bases: :py:obj:`CodingTemplate`


   Template for 16-bit signed integer parsing (-32768 to 32767).


   .. py:property:: data_size
      :type: int


      2 bytes.

      :type: Size


   .. py:method:: decode_value(data: bytearray, offset: int = 0, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> int

      Parse 16-bit signed integer.



   .. py:method:: encode_value(value: int) -> bytearray

      Encode sint16 value to bytes.



.. py:class:: Uint32Template

   Bases: :py:obj:`CodingTemplate`


   Template for 32-bit unsigned integer parsing.


   .. py:property:: data_size
      :type: int


      4 bytes.

      :type: Size


   .. py:method:: decode_value(data: bytearray, offset: int = 0, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> int

      Parse 32-bit unsigned integer.



   .. py:method:: encode_value(value: int) -> bytearray

      Encode uint32 value to bytes.



.. py:class:: ScaledUint16Template(scale_factor: float = 1.0, offset: int = 0)

   Bases: :py:obj:`ScaledTemplate`


   Template for scaled 16-bit unsigned integer.

   Used for values that need decimal precision encoded as integers.
   Can be initialized with scale_factor/offset or Bluetooth SIG M, d, b parameters.
   Formula: value = scale_factor * (raw + offset) or value = M * 10^d * (raw + b)
   Example: Temperature 25.5°C stored as 2550 with scale_factor=0.01, offset=0 or M=1, d=-2, b=0


   .. py:property:: data_size
      :type: int


      2 bytes.

      :type: Size


.. py:class:: ScaledSint16Template(scale_factor: float = 0.01, offset: int = 0)

   Bases: :py:obj:`ScaledTemplate`


   Template for scaled 16-bit signed integer.

   Used for signed values that need decimal precision encoded as integers.
   Can be initialized with scale_factor/offset or Bluetooth SIG M, d, b parameters.
   Formula: value = scale_factor * (raw + offset) or value = M * 10^d * (raw + b)
   Example: Temperature -10.5°C stored as -1050 with scale_factor=0.01, offset=0 or M=1, d=-2, b=0


   .. py:property:: data_size
      :type: int


      2 bytes.

      :type: Size


.. py:class:: ScaledSint8Template(scale_factor: float = 1.0, offset: int = 0)

   Bases: :py:obj:`ScaledTemplate`


   Template for scaled 8-bit signed integer.

   Used for signed values that need decimal precision encoded as integers.
   Can be initialized with scale_factor/offset or Bluetooth SIG M, d, b parameters.
   Formula: value = scale_factor * (raw + offset) or value = M * 10^d * (raw + b)
   Example: Temperature with scale_factor=0.01, offset=0 or M=1, d=-2, b=0


   .. py:property:: data_size
      :type: int


      1 byte.

      :type: Size


.. py:class:: ScaledUint32Template(scale_factor: float = 0.1, offset: int = 0)

   Bases: :py:obj:`ScaledTemplate`


   Template for scaled 32-bit unsigned integer with configurable resolution and offset.


   .. py:property:: data_size
      :type: int


      4 bytes.

      :type: Size


.. py:class:: ScaledUint24Template(scale_factor: float = 1.0, offset: int = 0)

   Bases: :py:obj:`ScaledTemplate`


   Template for scaled 24-bit unsigned integer with configurable resolution and offset.

   Used for values encoded in 3 bytes as unsigned integers.
   Example: Illuminance 1000 lux stored as bytes with scale_factor=1.0, offset=0


   .. py:property:: data_size
      :type: int


      3 bytes.

      :type: Size


.. py:class:: ScaledSint24Template(scale_factor: float = 0.01, offset: int = 0)

   Bases: :py:obj:`ScaledTemplate`


   Template for scaled 24-bit signed integer with configurable resolution and offset.

   Used for signed values encoded in 3 bytes.
   Example: Elevation 500.00m stored as bytes with scale_factor=0.01, offset=0


   .. py:property:: data_size
      :type: int


      3 bytes.

      :type: Size


.. py:class:: PercentageTemplate

   Bases: :py:obj:`CodingTemplate`


   Template for percentage values (0-100%) using uint8.


   .. py:property:: data_size
      :type: int


      1 byte.

      :type: Size


   .. py:method:: decode_value(data: bytearray, offset: int = 0, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> int

      Parse percentage value.



   .. py:method:: encode_value(value: int) -> bytearray

      Encode percentage value to bytes.



.. py:class:: TemperatureTemplate

   Bases: :py:obj:`CodingTemplate`


   Template for standard Bluetooth SIG temperature format (sint16, 0.01°C resolution).


   .. py:property:: data_size
      :type: int


      2 bytes.

      :type: Size


   .. py:method:: decode_value(data: bytearray, offset: int = 0, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> float

      Parse temperature in 0.01°C resolution.



   .. py:method:: encode_value(value: float) -> bytearray

      Encode temperature to bytes.



.. py:class:: ConcentrationTemplate(resolution: float = 1.0)

   Bases: :py:obj:`CodingTemplate`


   Template for concentration measurements with configurable resolution.

   Used for environmental sensors like CO2, VOC, particulate matter, etc.


   .. py:method:: from_letter_method(M: int, d: int, b: int = 0) -> ConcentrationTemplate
      :classmethod:


      Create instance using Bluetooth SIG M, d, b parameters.

      :param M: Multiplier factor
      :param d: Decimal exponent (10^d)
      :param b: Offset to add to raw value before scaling

      :returns: ConcentrationTemplate instance



   .. py:property:: data_size
      :type: int


      2 bytes.

      :type: Size


   .. py:method:: decode_value(data: bytearray, offset: int = 0, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> float

      Parse concentration with resolution.



   .. py:method:: encode_value(value: float) -> bytearray

      Encode concentration value to bytes.



.. py:class:: PressureTemplate

   Bases: :py:obj:`CodingTemplate`


   Template for pressure measurements (uint32, 0.1 Pa resolution).


   .. py:property:: data_size
      :type: int


      4 bytes.

      :type: Size


   .. py:method:: decode_value(data: bytearray, offset: int = 0, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> float

      Parse pressure in 0.1 Pa resolution (returns Pa).



   .. py:method:: encode_value(value: float) -> bytearray

      Encode pressure to bytes.



.. py:class:: TimeDataTemplate

   Bases: :py:obj:`CodingTemplate`


   Template for Bluetooth SIG time data parsing (10 bytes).

   Used for Current Time and Time with DST characteristics.
   Structure: Date Time (7 bytes) + Day of Week (1) + Fractions256 (1) + Adjust Reason (1)


   .. py:attribute:: LENGTH
      :value: 10



   .. py:attribute:: DAY_OF_WEEK_MAX
      :value: 7



   .. py:attribute:: FRACTIONS256_MAX
      :value: 255



   .. py:attribute:: ADJUST_REASON_MAX
      :value: 255



   .. py:property:: data_size
      :type: int


      10 bytes.

      :type: Size


   .. py:method:: decode_value(data: bytearray, offset: int = 0, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> TimeData

      Parse time data from bytes.



   .. py:method:: encode_value(value: TimeData) -> bytearray

      Encode time data to bytes.



.. py:class:: IEEE11073FloatTemplate

   Bases: :py:obj:`CodingTemplate`


   Template for IEEE 11073 SFLOAT format (16-bit medical device float).


   .. py:property:: data_size
      :type: int


      2 bytes.

      :type: Size


   .. py:method:: decode_value(data: bytearray, offset: int = 0, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> float

      Parse IEEE 11073 SFLOAT format.



   .. py:method:: encode_value(value: float) -> bytearray

      Encode value to IEEE 11073 SFLOAT format.



.. py:class:: Float32Template

   Bases: :py:obj:`CodingTemplate`


   Template for IEEE-754 32-bit float parsing.


   .. py:property:: data_size
      :type: int


      4 bytes.

      :type: Size


   .. py:method:: decode_value(data: bytearray, offset: int = 0, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> float

      Parse IEEE-754 32-bit float.



   .. py:method:: encode_value(value: float) -> bytearray

      Encode float32 value to bytes.



.. py:class:: Utf8StringTemplate(max_length: int = 256)

   Bases: :py:obj:`CodingTemplate`


   Template for UTF-8 string parsing with variable length.


   .. py:attribute:: max_length
      :value: 256



   .. py:property:: data_size
      :type: int


      Variable (0 to max_length).

      :type: Size


   .. py:method:: decode_value(data: bytearray, offset: int = 0, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> str

      Parse UTF-8 string from remaining data.



   .. py:method:: encode_value(value: str) -> bytearray

      Encode string to UTF-8 bytes.



.. py:class:: VectorTemplate

   Bases: :py:obj:`CodingTemplate`


   Template for 3D vector measurements (x, y, z float32 components).


   .. py:property:: data_size
      :type: int


      12 bytes (3 x float32).

      :type: Size


   .. py:method:: decode_value(data: bytearray, offset: int = 0, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> VectorData

      Parse 3D vector data.



   .. py:method:: encode_value(value: VectorData) -> bytearray

      Encode 3D vector data to bytes.



.. py:class:: Vector2DTemplate

   Bases: :py:obj:`CodingTemplate`


   Template for 2D vector measurements (x, y float32 components).


   .. py:property:: data_size
      :type: int


      8 bytes (2 x float32).

      :type: Size


   .. py:method:: decode_value(data: bytearray, offset: int = 0, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> Vector2DData

      Parse 2D vector data.



   .. py:method:: encode_value(value: Vector2DData) -> bytearray

      Encode 2D vector data to bytes.



