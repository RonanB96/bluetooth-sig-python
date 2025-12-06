src.bluetooth_sig.gatt.characteristics.linear_position
======================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.linear_position

.. autoapi-nested-parse::

   Linear Position characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.linear_position.LinearPositionCharacteristic
   src.bluetooth_sig.gatt.characteristics.linear_position.LinearPositionValues


Module Contents
---------------

.. py:class:: LinearPositionCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Linear Position characteristic (0x2C08).

   org.bluetooth.characteristic.linear_position

   The Linear Position characteristic is used to represent the linear position of an object
   along a given axis and referencing to the device-specific zero point.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> float | None

      Decode linear position characteristic.

      Decodes a 32-bit signed integer representing position in 10^-7 m increments
      per Bluetooth SIG Linear Position characteristic specification.

      :param data: Raw bytes from BLE characteristic (exactly 4 bytes, little-endian)
      :param ctx: Optional context for parsing (device info, flags, etc.)

      :returns: Position in meters, or None if value is not known

      :raises InsufficientDataError: If data is not exactly 4 bytes



   .. py:method:: encode_value(data: float) -> bytearray

      Encode linear position value.



.. py:class:: LinearPositionValues

   Special values for Linear Position characteristic per Bluetooth SIG specification.


   .. py:attribute:: VALUE_NOT_KNOWN
      :value: 2147483647



