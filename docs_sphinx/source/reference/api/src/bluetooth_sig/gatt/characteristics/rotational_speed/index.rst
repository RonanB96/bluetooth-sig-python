src.bluetooth_sig.gatt.characteristics.rotational_speed
=======================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.rotational_speed

.. autoapi-nested-parse::

   Rotational Speed characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.rotational_speed.RotationalSpeedValues
   src.bluetooth_sig.gatt.characteristics.rotational_speed.RotationalSpeedCharacteristic


Module Contents
---------------

.. py:class:: RotationalSpeedValues

   Special values for Rotational Speed characteristic per Bluetooth SIG specification.


   .. py:attribute:: VALUE_NOT_KNOWN
      :value: 2147483647



.. py:class:: RotationalSpeedCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Rotational Speed characteristic (0x2C09).

   org.bluetooth.characteristic.rotational_speed

   The Rotational Speed characteristic is used to represent the rotational speed of an object
   rotating around a device-specific axis.


   .. py:attribute:: expected_length
      :value: 4



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> float | None

      Decode rotational speed characteristic.

      Decodes a 32-bit signed integer representing speed in RPM
      per Bluetooth SIG Rotational Speed characteristic specification.

      :param data: Raw bytes from BLE characteristic (exactly 4 bytes, little-endian)
      :param ctx: Optional context for parsing (device info, flags, etc.)

      :returns: Rotational speed in revolutions per minute (RPM), or None if value is not known

      :raises InsufficientDataError: If data is not exactly 4 bytes



   .. py:method:: encode_value(data: float) -> bytearray

      Encode rotational speed value.



