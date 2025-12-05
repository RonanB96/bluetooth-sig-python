src.bluetooth_sig.gatt.characteristics.barometric_pressure_trend
================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.barometric_pressure_trend

.. autoapi-nested-parse::

   Barometric Pressure Trend characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.barometric_pressure_trend.BarometricPressureTrend
   src.bluetooth_sig.gatt.characteristics.barometric_pressure_trend.BarometricPressureTrendCharacteristic


Module Contents
---------------

.. py:class:: BarometricPressureTrend

   Bases: :py:obj:`enum.IntEnum`


   Barometric pressure trend enumeration.


   .. py:attribute:: UNKNOWN
      :value: 0



   .. py:attribute:: CONTINUOUSLY_FALLING
      :value: 1



   .. py:attribute:: CONTINUOUSLY_RISING
      :value: 2



   .. py:attribute:: FALLING_THEN_STEADY
      :value: 3



   .. py:attribute:: RISING_THEN_STEADY
      :value: 4



   .. py:attribute:: FALLING_BEFORE_LESSER_RISE
      :value: 5



   .. py:attribute:: FALLING_BEFORE_GREATER_RISE
      :value: 6



   .. py:attribute:: RISING_BEFORE_GREATER_FALL
      :value: 7



   .. py:attribute:: RISING_BEFORE_LESSER_FALL
      :value: 8



   .. py:attribute:: STEADY
      :value: 9



   .. py:method:: from_value(value: int) -> BarometricPressureTrend
      :classmethod:


      Create enum from integer value with fallback to UNKNOWN.



.. py:class:: BarometricPressureTrendCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Barometric Pressure Trend characteristic (0x2AA3).

   org.bluetooth.characteristic.barometric_pressure_trend

   Barometric pressure trend characteristic.

   Represents the trend observed for barometric pressure using
   enumerated values.


   .. py:attribute:: enum_class


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> BarometricPressureTrend

      Parse barometric pressure trend and return enum.

      Maps reserved value (0xFF) and invalid values to UNKNOWN.



   .. py:method:: encode_value(data: BarometricPressureTrend | int) -> bytearray

      Encode barometric pressure trend enum to bytes.



