src.bluetooth_sig.gatt.characteristics.utils.data_parser
========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.utils.data_parser

.. autoapi-nested-parse::

   Data parsing utilities for basic data types.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.utils.data_parser.DataParser


Module Contents
---------------

.. py:class:: DataParser

   Utility class for basic data type parsing and encoding.


   .. py:method:: encode_float32(value: float) -> bytearray
      :staticmethod:


      Encode IEEE-754 32-bit float (little-endian).



   .. py:method:: encode_float64(value: float) -> bytearray
      :staticmethod:


      Encode IEEE-754 64-bit double (little-endian).



   .. py:method:: encode_int16(value: int, signed: bool = False, endian: Literal['little', 'big'] = 'little') -> bytearray
      :staticmethod:


      Encode 16-bit integer with configurable endianness and signed/unsigned validation.



   .. py:method:: encode_int24(value: int, signed: bool = False, endian: Literal['little', 'big'] = 'little') -> bytearray
      :staticmethod:


      Encode 24-bit integer with configurable endianness and signed/unsigned validation.



   .. py:method:: encode_int32(value: int, signed: bool = False, endian: Literal['little', 'big'] = 'little') -> bytearray
      :staticmethod:


      Encode 32-bit integer with configurable endianness and signed/unsigned validation.



   .. py:method:: encode_int8(value: int, signed: bool = False) -> bytearray
      :staticmethod:


      Encode 8-bit integer with signed/unsigned validation.



   .. py:method:: parse_float32(data: bytearray, offset: int = 0) -> float
      :staticmethod:


      Parse IEEE-754 32-bit float (little-endian).



   .. py:method:: parse_float64(data: bytearray, offset: int = 0) -> float
      :staticmethod:


      Parse IEEE-754 64-bit double (little-endian).



   .. py:method:: parse_int16(data: bytes | bytearray, offset: int = 0, signed: bool = False, endian: Literal['little', 'big'] = 'little') -> int
      :staticmethod:


      Parse 16-bit integer with configurable endianness and signed interpretation.



   .. py:method:: parse_int24(data: bytes | bytearray, offset: int = 0, signed: bool = False, endian: Literal['little', 'big'] = 'little') -> int
      :staticmethod:


      Parse 24-bit integer with configurable endianness and signed interpretation.



   .. py:method:: parse_int32(data: bytes | bytearray, offset: int = 0, signed: bool = False, endian: Literal['little', 'big'] = 'little') -> int
      :staticmethod:


      Parse 32-bit integer with configurable endianness and signed interpretation.



   .. py:method:: parse_int8(data: bytes | bytearray, offset: int = 0, signed: bool = False) -> int
      :staticmethod:


      Parse 8-bit integer with optional signed interpretation.



   .. py:method:: parse_utf8_string(data: bytearray) -> str
      :staticmethod:


      Parse UTF-8 string from bytearray with null termination handling.



   .. py:method:: parse_variable_length(data: bytes | bytearray, min_length: int, max_length: int) -> bytes
      :staticmethod:


      Parse variable length data with validation.



