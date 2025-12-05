src.bluetooth_sig.gatt.characteristics.force
============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.force

.. autoapi-nested-parse::

   Force characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.force.ForceValues
   src.bluetooth_sig.gatt.characteristics.force.ForceCharacteristic


Module Contents
---------------

.. py:class:: ForceValues

   Special values for Force characteristic per Bluetooth SIG specification.


   .. py:attribute:: VALUE_NOT_KNOWN
      :value: 2147483647



.. py:class:: ForceCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Force characteristic (0x2C07).

   org.bluetooth.characteristic.force

   The Force characteristic is used to represent the force being applied to an object along a given axis.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> float | None

      Decode force characteristic.

      Decodes a 32-bit signed integer representing force in 0.001 N increments
      per Bluetooth SIG Force characteristic specification.

      :param data: Raw bytes from BLE characteristic (exactly 4 bytes, little-endian)
      :param ctx: Optional context for parsing (device info, flags, etc.)

      :returns: Force in Newtons, or None if value is not known

      :raises InsufficientDataError: If data is not exactly 4 bytes



   .. py:method:: encode_value(data: float) -> bytearray

      Encode force value.



