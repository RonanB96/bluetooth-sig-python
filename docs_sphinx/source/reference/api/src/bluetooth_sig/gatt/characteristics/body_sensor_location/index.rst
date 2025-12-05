src.bluetooth_sig.gatt.characteristics.body_sensor_location
===========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.body_sensor_location

.. autoapi-nested-parse::

   Body Sensor Location characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.body_sensor_location.BodySensorLocation
   src.bluetooth_sig.gatt.characteristics.body_sensor_location.BodySensorLocationCharacteristic


Module Contents
---------------

.. py:class:: BodySensorLocation

   Bases: :py:obj:`enum.IntEnum`


   Body sensor location enumeration (0x2A38).


   .. py:attribute:: OTHER
      :value: 0



   .. py:attribute:: CHEST
      :value: 1



   .. py:attribute:: WRIST
      :value: 2



   .. py:attribute:: FINGER
      :value: 3



   .. py:attribute:: HAND
      :value: 4



   .. py:attribute:: EAR_LOBE
      :value: 5



   .. py:attribute:: FOOT
      :value: 6



.. py:class:: BodySensorLocationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Body Sensor Location characteristic (0x2A38).

   Represents the location of a sensor on the human body.
   Used primarily with heart rate and other health monitoring devices.

   Spec: Bluetooth SIG Assigned Numbers, Body Sensor Location characteristic


   .. py:method:: decode_value(data: bytearray, ctx: bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> BodySensorLocation

      Decode body sensor location from raw bytes.

      :param data: Raw bytes from BLE characteristic (1 byte)
      :param ctx: Unused, for signature compatibility

      :returns: BodySensorLocation enum value

      :raises ValueError: If data length is not exactly 1 byte or value is invalid



   .. py:method:: encode_value(data: BodySensorLocation) -> bytearray

      Encode body sensor location to bytes.

      :param data: BodySensorLocation enum value

      :returns: Encoded bytes (1 byte)



