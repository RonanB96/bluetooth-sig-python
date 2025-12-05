src.bluetooth_sig.gatt.characteristics.longitude
================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.longitude

.. autoapi-nested-parse::

   Longitude characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.longitude.LongitudeCharacteristic


Module Contents
---------------

.. py:class:: LongitudeCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Longitude characteristic (0x2AAF).

   org.bluetooth.characteristic.longitude

   Longitude characteristic.


   .. py:attribute:: BYTE_LENGTH
      :value: 4



   .. py:attribute:: DEGREE_SCALING_FACTOR
      :value: 1e-07



   .. py:attribute:: LONGITUDE_MIN
      :value: -180.0



   .. py:attribute:: LONGITUDE_MAX
      :value: 180.0



   .. py:attribute:: expected_length
      :value: 4



   .. py:attribute:: min_value
      :value: -180.0



   .. py:attribute:: max_value
      :value: 180.0



   .. py:attribute:: expected_type


   .. py:method:: decode_value(data: bytearray, ctx: bluetooth_sig.types.context.CharacteristicContext | None = None) -> float

      Parse longitude from sint32 * 10^-7 degrees.



   .. py:method:: encode_value(data: float) -> bytearray

      Encode longitude to sint32 * 10^-7 degrees.



