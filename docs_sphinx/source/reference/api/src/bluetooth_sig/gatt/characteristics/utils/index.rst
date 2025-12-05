src.bluetooth_sig.gatt.characteristics.utils
============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.utils

.. autoapi-nested-parse::

   Utility classes for GATT characteristic parsing and encoding.

   This module provides organized utility classes that characteristics can
   import and use as needed, maintaining logical grouping of functionality
   while avoiding multiple inheritance complexity.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /reference/api/src/bluetooth_sig/gatt/characteristics/utils/bit_field_utils/index
   /reference/api/src/bluetooth_sig/gatt/characteristics/utils/data_parser/index
   /reference/api/src/bluetooth_sig/gatt/characteristics/utils/data_validator/index
   /reference/api/src/bluetooth_sig/gatt/characteristics/utils/debug_utils/index
   /reference/api/src/bluetooth_sig/gatt/characteristics/utils/ieee11073_parser/index
   /reference/api/src/bluetooth_sig/gatt/characteristics/utils/parse_trace/index


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.utils.BitFieldUtils
   src.bluetooth_sig.gatt.characteristics.utils.DataParser
   src.bluetooth_sig.gatt.characteristics.utils.DataValidator
   src.bluetooth_sig.gatt.characteristics.utils.DebugUtils
   src.bluetooth_sig.gatt.characteristics.utils.IEEE11073Parser
   src.bluetooth_sig.gatt.characteristics.utils.ParseTrace


Package Contents
----------------

.. py:class:: BitFieldUtils

   Utility class for bit field manipulation and flag handling.


   .. py:attribute:: SINGLE_BIT_MASK
      :value: 1



   .. py:attribute:: DEFAULT_BIT_WIDTH
      :value: 32



   .. py:method:: extract_bit_field(value: int, start_bit: int, num_bits: int) -> int
      :staticmethod:


      Extract a bit field from an integer value.



   .. py:method:: set_bit_field(value: int, field_value: int, start_bit: int, num_bits: int) -> int
      :staticmethod:


      Set a bit field in an integer value.



   .. py:method:: create_bitmask(start_bit: int, num_bits: int) -> int
      :staticmethod:


      Create a bitmask for a specific bit field range.



   .. py:method:: test_bit(value: int, bit_position: int) -> bool
      :staticmethod:


      Test if a specific bit is set in the value.



   .. py:method:: test_bits_any(value: int, bitmask: int) -> bool
      :staticmethod:


      Test if any bits in the bitmask are set in the value.



   .. py:method:: test_bits_all(value: int, bitmask: int) -> bool
      :staticmethod:


      Test if all bits in the bitmask are set in the value.



   .. py:method:: set_bit(value: int, bit_position: int) -> int
      :staticmethod:


      Set a specific bit in the value.



   .. py:method:: clear_bit(value: int, bit_position: int) -> int
      :staticmethod:


      Clear a specific bit in the value.



   .. py:method:: toggle_bit(value: int, bit_position: int) -> int
      :staticmethod:


      Toggle a specific bit in the value.



   .. py:method:: extract_bits(value: int, bitmask: int) -> int
      :staticmethod:


      Extract bits from value using a bitmask.



   .. py:method:: set_bits(value: int, bitmask: int) -> int
      :staticmethod:


      Set all bits specified in the bitmask.



   .. py:method:: clear_bits(value: int, bitmask: int) -> int
      :staticmethod:


      Clear all bits specified in the bitmask.



   .. py:method:: toggle_bits(value: int, bitmask: int) -> int
      :staticmethod:


      Toggle all bits specified in the bitmask.



   .. py:method:: count_set_bits(value: int) -> int
      :staticmethod:


      Count the number of set bits in the value.



   .. py:method:: get_bit_positions(value: int) -> list[int]
      :staticmethod:


      Get a list of positions of all set bits in the value.



   .. py:method:: find_first_set_bit(value: int) -> int | None
      :staticmethod:


      Find the position of the first (least significant) set bit.



   .. py:method:: find_last_set_bit(value: int) -> int | None
      :staticmethod:


      Find the position of the last (most significant) set bit.



   .. py:method:: reverse_bits(value: int, bit_width: int = DEFAULT_BIT_WIDTH) -> int
      :staticmethod:


      Reverse the bits in a value within the specified bit width.



   .. py:method:: calculate_parity(value: int) -> int
      :staticmethod:


      Calculate the parity (even/odd) of set bits.

      Returns 0 for even, 1 for odd.



   .. py:method:: validate_bit_field_range(start_bit: int, num_bits: int, total_bits: int = DEFAULT_BIT_WIDTH) -> bool
      :staticmethod:


      Validate that a bit field range is within bounds.



   .. py:method:: copy_bit_field(source: int, dest: int, source_start: int, dest_start: int, num_bits: int) -> int
      :staticmethod:


      Copy a bit field from source to destination.



   .. py:method:: shift_bit_field_left(value: int, start_bit: int, num_bits: int, shift_amount: int) -> int
      :staticmethod:


      Shift a bit field left within the value.



   .. py:method:: shift_bit_field_right(value: int, start_bit: int, num_bits: int, shift_amount: int) -> int
      :staticmethod:


      Shift a bit field right within the value.



   .. py:method:: merge_bit_fields(*fields: tuple[int, int, int]) -> int
      :staticmethod:


      Merge multiple bit fields into a single value.

      :param fields: Tuples of (field_value, start_bit, num_bits)



   .. py:method:: split_bit_field(value: int, *field_specs: tuple[int, int]) -> list[int]
      :staticmethod:


      Split a value into multiple bit fields.

      :param value: The value to split
      :param field_specs: Tuples of (start_bit, num_bits) for each field

      :returns: List of extracted field values



   .. py:method:: compare_bit_fields(value1: int, value2: int, start_bit: int, num_bits: int) -> int
      :staticmethod:


      Compare bit fields between two values.

      Returns -1, 0, or 1.



   .. py:method:: rotate_left(value: int, positions: int, bit_width: int = DEFAULT_BIT_WIDTH) -> int
      :staticmethod:


      Rotate bits left by the specified number of positions.



   .. py:method:: rotate_right(value: int, positions: int, bit_width: int = DEFAULT_BIT_WIDTH) -> int
      :staticmethod:


      Rotate bits right by the specified number of positions.



   .. py:method:: extract_bit_field_from_mask(value: int, mask: int, shift: int) -> int
      :staticmethod:


      Extract a bit field using a mask and shift amount.

      :param value: The value to extract from
      :param mask: The base mask (e.g., 0x0F for 4 bits)
      :param shift: How many bits to shift the mask left

      :returns: The extracted bit field value



.. py:class:: DataParser

   Utility class for basic data type parsing and encoding.


   .. py:method:: parse_int8(data: bytes | bytearray, offset: int = 0, signed: bool = False) -> int
      :staticmethod:


      Parse 8-bit integer with optional signed interpretation.



   .. py:method:: parse_int16(data: bytes | bytearray, offset: int = 0, signed: bool = False, endian: Literal['little', 'big'] = 'little') -> int
      :staticmethod:


      Parse 16-bit integer with configurable endianness and signed interpretation.



   .. py:method:: parse_int32(data: bytes | bytearray, offset: int = 0, signed: bool = False, endian: Literal['little', 'big'] = 'little') -> int
      :staticmethod:


      Parse 32-bit integer with configurable endianness and signed interpretation.



   .. py:method:: parse_int24(data: bytes | bytearray, offset: int = 0, signed: bool = False, endian: Literal['little', 'big'] = 'little') -> int
      :staticmethod:


      Parse 24-bit integer with configurable endianness and signed interpretation.



   .. py:method:: parse_float32(data: bytearray, offset: int = 0) -> float
      :staticmethod:


      Parse IEEE-754 32-bit float (little-endian).



   .. py:method:: parse_float64(data: bytearray, offset: int = 0) -> float
      :staticmethod:


      Parse IEEE-754 64-bit double (little-endian).



   .. py:method:: parse_utf8_string(data: bytearray) -> str
      :staticmethod:


      Parse UTF-8 string from bytearray with null termination handling.



   .. py:method:: parse_variable_length(data: bytes | bytearray, min_length: int, max_length: int) -> bytes
      :staticmethod:


      Parse variable length data with validation.



   .. py:method:: encode_int8(value: int, signed: bool = False) -> bytearray
      :staticmethod:


      Encode 8-bit integer with signed/unsigned validation.



   .. py:method:: encode_int16(value: int, signed: bool = False, endian: Literal['little', 'big'] = 'little') -> bytearray
      :staticmethod:


      Encode 16-bit integer with configurable endianness and signed/unsigned validation.



   .. py:method:: encode_int32(value: int, signed: bool = False, endian: Literal['little', 'big'] = 'little') -> bytearray
      :staticmethod:


      Encode 32-bit integer with configurable endianness and signed/unsigned validation.



   .. py:method:: encode_int24(value: int, signed: bool = False, endian: Literal['little', 'big'] = 'little') -> bytearray
      :staticmethod:


      Encode 24-bit integer with configurable endianness and signed/unsigned validation.



   .. py:method:: encode_float32(value: float) -> bytearray
      :staticmethod:


      Encode IEEE-754 32-bit float (little-endian).



   .. py:method:: encode_float64(value: float) -> bytearray
      :staticmethod:


      Encode IEEE-754 64-bit double (little-endian).



.. py:class:: DataValidator

   Utility class for data validation and integrity checking.


   .. py:method:: validate_data_length(data: bytearray, expected_min: int, expected_max: int | None = None) -> None
      :staticmethod:


      Validate data length against expected range.



   .. py:method:: validate_range(value: int | float, min_val: int | float, max_val: int | float) -> None
      :staticmethod:


      Validate that a value is within the specified range.



   .. py:method:: validate_enum_value(value: int, enum_class: type[enum.IntEnum]) -> None
      :staticmethod:


      Validate that a value is a valid member of an IntEnum.



   .. py:method:: validate_concentration_range(value: float, max_ppm: float = MAX_CONCENTRATION_PPM) -> None
      :staticmethod:


      Validate concentration value is in acceptable range.



   .. py:method:: validate_temperature_range(value: float, min_celsius: float = ABSOLUTE_ZERO_CELSIUS, max_celsius: float = MAX_TEMPERATURE_CELSIUS) -> None
      :staticmethod:


      Validate temperature is in physically reasonable range.



   .. py:method:: validate_percentage(value: int | float, allow_over_100: bool = False) -> None
      :staticmethod:


      Validate percentage value (0-100% or 0-200% for some characteristics).



   .. py:method:: validate_power_range(value: int | float, max_watts: float = MAX_POWER_WATTS) -> None
      :staticmethod:


      Validate power measurement range.



.. py:class:: DebugUtils

   Utility class for debugging and testing support.


   .. py:attribute:: HEX_FORMAT_WIDTH
      :value: 2



   .. py:attribute:: DEFAULT_PRECISION
      :value: 2



   .. py:method:: format_hex_dump(data: bytearray) -> str
      :staticmethod:


      Format data as a hex dump for debugging.



   .. py:method:: validate_round_trip(characteristic: bluetooth_sig.types.protocols.CharacteristicProtocol, original_data: bytearray) -> bool
      :staticmethod:


      Validate that parse/encode operations preserve data integrity.



   .. py:method:: format_measurement_value(value: int | float | str | None, unit: str | None = None, precision: int = 2) -> str
      :staticmethod:


      Format measurement value with unit for display.



   .. py:method:: format_hex_data(data: bytes | bytearray, separator: str = ' ') -> str
      :staticmethod:


      Format binary data as hex string.



   .. py:method:: format_binary_flags(value: int, bit_names: list[str]) -> str
      :staticmethod:


      Format integer as binary flags with names.



   .. py:method:: validate_struct_format(data: bytes | bytearray, format_string: str) -> None
      :staticmethod:


      Validate data length matches struct format requirements.



   .. py:method:: format_field_error(error: bluetooth_sig.types.data_types.ParseFieldError, data: bytes | bytearray) -> str
      :staticmethod:


      Format a field-level parsing error with context.

      :param error: The ParseFieldError to format
      :param data: Complete raw data for context

      :returns: Formatted error message with hex dump and field context



   .. py:method:: format_field_errors(errors: list[Any], data: bytes | bytearray) -> str
      :staticmethod:


      Format multiple field errors into a readable message.

      :param errors: List of ParseFieldError objects
      :param data: Complete raw data for context

      :returns: Formatted string with all field errors and context



   .. py:method:: format_parse_trace(trace: list[str]) -> str
      :staticmethod:


      Format parse trace as readable steps.

      :param trace: List of parse trace entries

      :returns: Formatted trace string



.. py:class:: IEEE11073Parser

   Utility class for IEEE-11073 medical device format support.


   .. py:attribute:: SFLOAT_MANTISSA_MASK
      :value: 4095



   .. py:attribute:: SFLOAT_MANTISSA_SIGN_BIT
      :value: 2048



   .. py:attribute:: SFLOAT_MANTISSA_CONVERSION
      :value: 4096



   .. py:attribute:: SFLOAT_EXPONENT_MASK
      :value: 15



   .. py:attribute:: SFLOAT_EXPONENT_SIGN_BIT
      :value: 8



   .. py:attribute:: SFLOAT_EXPONENT_CONVERSION
      :value: 16



   .. py:attribute:: SFLOAT_MANTISSA_MAX
      :value: 2048



   .. py:attribute:: SFLOAT_EXPONENT_MIN
      :value: -8



   .. py:attribute:: SFLOAT_EXPONENT_MAX
      :value: 7



   .. py:attribute:: SFLOAT_EXPONENT_BIAS
      :value: 8



   .. py:attribute:: SFLOAT_MANTISSA_START_BIT
      :value: 0



   .. py:attribute:: SFLOAT_MANTISSA_BIT_WIDTH
      :value: 12



   .. py:attribute:: SFLOAT_EXPONENT_START_BIT
      :value: 12



   .. py:attribute:: SFLOAT_EXPONENT_BIT_WIDTH
      :value: 4



   .. py:attribute:: SFLOAT_NAN
      :value: 2047



   .. py:attribute:: SFLOAT_NRES
      :value: 2048



   .. py:attribute:: SFLOAT_POSITIVE_INFINITY
      :value: 2046



   .. py:attribute:: SFLOAT_NEGATIVE_INFINITY
      :value: 2050



   .. py:attribute:: FLOAT32_NAN
      :value: 8388607



   .. py:attribute:: FLOAT32_POSITIVE_INFINITY
      :value: 8388608



   .. py:attribute:: FLOAT32_NEGATIVE_INFINITY
      :value: 8388609



   .. py:attribute:: FLOAT32_NRES
      :value: 8388610



   .. py:attribute:: FLOAT32_MANTISSA_MASK
      :value: 16777215



   .. py:attribute:: FLOAT32_MANTISSA_SIGN_BIT
      :value: 8388608



   .. py:attribute:: FLOAT32_MANTISSA_CONVERSION
      :value: 16777216



   .. py:attribute:: FLOAT32_EXPONENT_MASK
      :value: 255



   .. py:attribute:: FLOAT32_EXPONENT_SIGN_BIT
      :value: 128



   .. py:attribute:: FLOAT32_EXPONENT_CONVERSION
      :value: 256



   .. py:attribute:: FLOAT32_MANTISSA_MAX
      :value: 8388608



   .. py:attribute:: FLOAT32_EXPONENT_MIN
      :value: -128



   .. py:attribute:: FLOAT32_EXPONENT_MAX
      :value: 127



   .. py:attribute:: FLOAT32_EXPONENT_BIAS
      :value: 128



   .. py:attribute:: FLOAT32_MANTISSA_START_BIT
      :value: 0



   .. py:attribute:: FLOAT32_MANTISSA_BIT_WIDTH
      :value: 24



   .. py:attribute:: FLOAT32_EXPONENT_START_BIT
      :value: 24



   .. py:attribute:: FLOAT32_EXPONENT_BIT_WIDTH
      :value: 8



   .. py:attribute:: IEEE11073_MIN_YEAR
      :value: 1582



   .. py:attribute:: MONTH_MIN
      :value: 1



   .. py:attribute:: MONTH_MAX
      :value: 12



   .. py:attribute:: DAY_MIN
      :value: 1



   .. py:attribute:: DAY_MAX
      :value: 31



   .. py:attribute:: HOUR_MIN
      :value: 0



   .. py:attribute:: HOUR_MAX
      :value: 23



   .. py:attribute:: MINUTE_MIN
      :value: 0



   .. py:attribute:: MINUTE_MAX
      :value: 59



   .. py:attribute:: SECOND_MIN
      :value: 0



   .. py:attribute:: SECOND_MAX
      :value: 59



   .. py:attribute:: TIMESTAMP_LENGTH
      :value: 7



   .. py:method:: parse_sfloat(data: bytes | bytearray, offset: int = 0) -> float
      :staticmethod:


      Parse IEEE 11073 16-bit SFLOAT.

      :param data: Raw bytes/bytearray
      :param offset: Offset in the data



   .. py:method:: parse_float32(data: bytes | bytearray, offset: int = 0) -> float
      :staticmethod:


      Parse IEEE 11073 32-bit FLOAT.



   .. py:method:: encode_sfloat(value: float) -> bytearray
      :staticmethod:


      Encode float to IEEE 11073 16-bit SFLOAT.



   .. py:method:: encode_float32(value: float) -> bytearray
      :staticmethod:


      Encode float to IEEE 11073 32-bit FLOAT.



   .. py:method:: parse_timestamp(data: bytearray, offset: int) -> datetime.datetime
      :staticmethod:


      Parse IEEE-11073 timestamp format (7 bytes).



   .. py:method:: encode_timestamp(timestamp: datetime.datetime) -> bytearray
      :staticmethod:


      Encode timestamp to IEEE-11073 7-byte format.



.. py:class:: ParseTrace(enabled: bool = True)

   Manages parse traces with built-in enable/disable logic.

   This class encapsulates the trace collection logic to avoid manual
   if checks throughout the parsing code, improving performance when
   tracing is disabled.

   .. admonition:: Example

      trace = ParseTrace(enabled=True)
      trace.append("Starting parse")
      trace.append("Validation complete")
      result = trace.get_trace()  # Returns list of strings


   .. py:method:: append(message: str) -> None

      Append a message to the trace if tracing is enabled.

      :param message: Trace message to append



   .. py:method:: get_trace() -> list[str]

      Get the collected trace messages.

      :returns: List of trace messages if enabled, empty list otherwise



   .. py:property:: enabled
      :type: bool


      Check if tracing is enabled.

      :returns: True if tracing is enabled, False otherwise


