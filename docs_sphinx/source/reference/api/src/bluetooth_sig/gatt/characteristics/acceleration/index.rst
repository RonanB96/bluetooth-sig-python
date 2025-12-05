src.bluetooth_sig.gatt.characteristics.acceleration
===================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.acceleration

.. autoapi-nested-parse::

   Acceleration characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.acceleration.AccelerationValues
   src.bluetooth_sig.gatt.characteristics.acceleration.AccelerationCharacteristic


Module Contents
---------------

.. py:class:: AccelerationValues

   Special values for Acceleration characteristic per Bluetooth SIG specification.


   .. py:attribute:: VALUE_NOT_KNOWN
      :value: 2147483647



.. py:class:: AccelerationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Acceleration characteristic (0x2C06).

   org.bluetooth.characteristic.acceleration

   The Acceleration characteristic is used to represent the acceleration of an object
   along a given axis as determined by the service.


   .. py:attribute:: expected_length
      :value: 4



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> float | None

      Decode acceleration characteristic.

      Decodes a 32-bit signed integer representing acceleration in 0.001 m/s² increments
      per Bluetooth SIG Acceleration characteristic specification.

      :param data: Raw bytes from BLE characteristic (exactly 4 bytes, little-endian)
      :param ctx: Optional context for parsing (device info, flags, etc.)

      :returns: Acceleration in meters per second squared, or None if value is not known

      :raises InsufficientDataError: If data is not exactly 4 bytes



   .. py:method:: encode_value(data: float) -> bytearray

      Encode acceleration value.



