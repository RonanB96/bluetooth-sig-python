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

.. py:class:: LongitudeCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Longitude characteristic (0x2AAF).

   org.bluetooth.characteristic.longitude

   Longitude characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: bluetooth_sig.types.context.CharacteristicContext | None = None) -> float

      Parse longitude from sint32 * 10^-7 degrees.



   .. py:method:: encode_value(data: float) -> bytearray

      Encode longitude to sint32 * 10^-7 degrees.



   .. py:attribute:: BYTE_LENGTH
      :value: 4



   .. py:attribute:: DEGREE_SCALING_FACTOR
      :value: 1e-07



   .. py:attribute:: LONGITUDE_MAX
      :value: 180.0



   .. py:attribute:: LONGITUDE_MIN
      :value: -180.0



   .. py:attribute:: expected_length
      :value: 4



   .. py:attribute:: expected_type


   .. py:attribute:: max_value
      :value: 180.0



   .. py:attribute:: min_value
      :value: -180.0



