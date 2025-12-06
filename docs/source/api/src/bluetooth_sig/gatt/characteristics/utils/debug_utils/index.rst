src.bluetooth_sig.gatt.characteristics.utils.debug_utils
========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.utils.debug_utils

.. autoapi-nested-parse::

   Debug utility methods for characteristic parsing.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.utils.debug_utils.DebugUtils


Module Contents
---------------

.. py:class:: DebugUtils

   Utility class for debugging and testing support.


   .. py:method:: format_binary_flags(value: int, bit_names: list[str]) -> str
      :staticmethod:


      Format integer as binary flags with names.



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



   .. py:method:: format_hex_data(data: bytes | bytearray, separator: str = ' ') -> str
      :staticmethod:


      Format binary data as hex string.



   .. py:method:: format_hex_dump(data: bytearray) -> str
      :staticmethod:


      Format data as a hex dump for debugging.



   .. py:method:: format_measurement_value(value: int | float | str | None, unit: str | None = None, precision: int = 2) -> str
      :staticmethod:


      Format measurement value with unit for display.



   .. py:method:: format_parse_trace(trace: list[str]) -> str
      :staticmethod:


      Format parse trace as readable steps.

      :param trace: List of parse trace entries

      :returns: Formatted trace string



   .. py:method:: validate_round_trip(characteristic: bluetooth_sig.types.protocols.CharacteristicProtocol, original_data: bytearray) -> bool
      :staticmethod:


      Validate that parse/encode operations preserve data integrity.



   .. py:method:: validate_struct_format(data: bytes | bytearray, format_string: str) -> None
      :staticmethod:


      Validate data length matches struct format requirements.



   .. py:attribute:: DEFAULT_PRECISION
      :value: 2



   .. py:attribute:: HEX_FORMAT_WIDTH
      :value: 2



