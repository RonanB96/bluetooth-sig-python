src.bluetooth_sig.gatt.characteristics.utils.ieee11073_parser
=============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.utils.ieee11073_parser

.. autoapi-nested-parse::

   IEEE 11073 medical device format support utilities.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.utils.ieee11073_parser.IEEE11073Parser


Module Contents
---------------

.. py:class:: IEEE11073Parser

   Utility class for IEEE-11073 medical device format support.


   .. py:method:: encode_float32(value: float) -> bytearray
      :staticmethod:


      Encode float to IEEE 11073 32-bit FLOAT.



   .. py:method:: encode_sfloat(value: float) -> bytearray
      :staticmethod:


      Encode float to IEEE 11073 16-bit SFLOAT.



   .. py:method:: encode_timestamp(timestamp: datetime.datetime) -> bytearray
      :staticmethod:


      Encode timestamp to IEEE-11073 7-byte format.



   .. py:method:: parse_float32(data: bytes | bytearray, offset: int = 0) -> float
      :staticmethod:


      Parse IEEE 11073 32-bit FLOAT.



   .. py:method:: parse_sfloat(data: bytes | bytearray, offset: int = 0) -> float
      :staticmethod:


      Parse IEEE 11073 16-bit SFLOAT.

      :param data: Raw bytes/bytearray
      :param offset: Offset in the data



   .. py:method:: parse_timestamp(data: bytearray, offset: int) -> datetime.datetime
      :staticmethod:


      Parse IEEE-11073 timestamp format (7 bytes).



   .. py:attribute:: DAY_MAX
      :value: 31



   .. py:attribute:: DAY_MIN
      :value: 1



   .. py:attribute:: FLOAT32_EXPONENT_BIAS
      :value: 128



   .. py:attribute:: FLOAT32_EXPONENT_BIT_WIDTH
      :value: 8



   .. py:attribute:: FLOAT32_EXPONENT_CONVERSION
      :value: 256



   .. py:attribute:: FLOAT32_EXPONENT_MASK
      :value: 255



   .. py:attribute:: FLOAT32_EXPONENT_MAX
      :value: 127



   .. py:attribute:: FLOAT32_EXPONENT_MIN
      :value: -128



   .. py:attribute:: FLOAT32_EXPONENT_SIGN_BIT
      :value: 128



   .. py:attribute:: FLOAT32_EXPONENT_START_BIT
      :value: 24



   .. py:attribute:: FLOAT32_MANTISSA_BIT_WIDTH
      :value: 24



   .. py:attribute:: FLOAT32_MANTISSA_CONVERSION
      :value: 16777216



   .. py:attribute:: FLOAT32_MANTISSA_MASK
      :value: 16777215



   .. py:attribute:: FLOAT32_MANTISSA_MAX
      :value: 8388608



   .. py:attribute:: FLOAT32_MANTISSA_SIGN_BIT
      :value: 8388608



   .. py:attribute:: FLOAT32_MANTISSA_START_BIT
      :value: 0



   .. py:attribute:: FLOAT32_NAN
      :value: 8388607



   .. py:attribute:: FLOAT32_NEGATIVE_INFINITY
      :value: 8388609



   .. py:attribute:: FLOAT32_NRES
      :value: 8388610



   .. py:attribute:: FLOAT32_POSITIVE_INFINITY
      :value: 8388608



   .. py:attribute:: HOUR_MAX
      :value: 23



   .. py:attribute:: HOUR_MIN
      :value: 0



   .. py:attribute:: IEEE11073_MIN_YEAR
      :value: 1582



   .. py:attribute:: MINUTE_MAX
      :value: 59



   .. py:attribute:: MINUTE_MIN
      :value: 0



   .. py:attribute:: MONTH_MAX
      :value: 12



   .. py:attribute:: MONTH_MIN
      :value: 1



   .. py:attribute:: SECOND_MAX
      :value: 59



   .. py:attribute:: SECOND_MIN
      :value: 0



   .. py:attribute:: SFLOAT_EXPONENT_BIAS
      :value: 8



   .. py:attribute:: SFLOAT_EXPONENT_BIT_WIDTH
      :value: 4



   .. py:attribute:: SFLOAT_EXPONENT_CONVERSION
      :value: 16



   .. py:attribute:: SFLOAT_EXPONENT_MASK
      :value: 15



   .. py:attribute:: SFLOAT_EXPONENT_MAX
      :value: 7



   .. py:attribute:: SFLOAT_EXPONENT_MIN
      :value: -8



   .. py:attribute:: SFLOAT_EXPONENT_SIGN_BIT
      :value: 8



   .. py:attribute:: SFLOAT_EXPONENT_START_BIT
      :value: 12



   .. py:attribute:: SFLOAT_MANTISSA_BIT_WIDTH
      :value: 12



   .. py:attribute:: SFLOAT_MANTISSA_CONVERSION
      :value: 4096



   .. py:attribute:: SFLOAT_MANTISSA_MASK
      :value: 4095



   .. py:attribute:: SFLOAT_MANTISSA_MAX
      :value: 2048



   .. py:attribute:: SFLOAT_MANTISSA_SIGN_BIT
      :value: 2048



   .. py:attribute:: SFLOAT_MANTISSA_START_BIT
      :value: 0



   .. py:attribute:: SFLOAT_NAN
      :value: 2047



   .. py:attribute:: SFLOAT_NEGATIVE_INFINITY
      :value: 2050



   .. py:attribute:: SFLOAT_NRES
      :value: 2048



   .. py:attribute:: SFLOAT_POSITIVE_INFINITY
      :value: 2046



   .. py:attribute:: TIMESTAMP_LENGTH
      :value: 7



