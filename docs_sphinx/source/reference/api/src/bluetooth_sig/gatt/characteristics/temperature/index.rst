src.bluetooth_sig.gatt.characteristics.temperature
==================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.temperature

.. autoapi-nested-parse::

   Temperature characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.temperature.TemperatureValues
   src.bluetooth_sig.gatt.characteristics.temperature.TemperatureCharacteristic


Module Contents
---------------

.. py:class:: TemperatureValues

   Special values for Temperature characteristic per Bluetooth SIG specification.


   .. py:attribute:: VALUE_UNKNOWN
      :value: -32768



.. py:class:: TemperatureCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Temperature characteristic (0x2A6E).

   org.bluetooth.characteristic.temperature

   Temperature measurement characteristic.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> float | None

      Decode temperature characteristic.

      Decodes a 16-bit signed integer representing temperature in 0.01°C increments
      per Bluetooth SIG Temperature characteristic specification.

      :param data: Raw bytes from BLE characteristic (exactly 2 bytes, little-endian)
      :param ctx: Optional context for parsing (device info, flags, etc.)

      :returns: Temperature in degrees Celsius, or None if value is unknown (-32768)

      :raises InsufficientDataError: If data is not exactly 2 bytes



   .. py:method:: encode_value(data: float) -> bytearray

      Encode temperature value.



