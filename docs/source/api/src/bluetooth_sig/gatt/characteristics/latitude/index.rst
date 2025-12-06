src.bluetooth_sig.gatt.characteristics.latitude
===============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.latitude

.. autoapi-nested-parse::

   Latitude characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.latitude.LatitudeCharacteristic


Module Contents
---------------

.. py:class:: LatitudeCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Latitude characteristic (0x2AAE).

   org.bluetooth.characteristic.latitude

   Latitude characteristic.


   .. py:method:: decode_value(data: bytearray, ctx: bluetooth_sig.types.context.CharacteristicContext | None = None) -> float

      Parse latitude from sint32 * 10^-7 degrees.



   .. py:method:: encode_value(data: float) -> bytearray

      Encode latitude to sint32 * 10^-7 degrees.



   .. py:attribute:: BYTE_LENGTH
      :value: 4



   .. py:attribute:: DEGREE_SCALING_FACTOR
      :value: 1e-07



   .. py:attribute:: LATITUDE_MAX
      :value: 90.0



   .. py:attribute:: LATITUDE_MIN
      :value: -90.0



   .. py:attribute:: expected_length
      :value: 4



   .. py:attribute:: expected_type


   .. py:attribute:: max_value
      :value: 90.0



   .. py:attribute:: min_value
      :value: -90.0



