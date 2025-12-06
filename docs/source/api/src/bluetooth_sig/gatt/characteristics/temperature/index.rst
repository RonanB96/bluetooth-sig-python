src.bluetooth_sig.gatt.characteristics.temperature
==================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.temperature

.. autoapi-nested-parse::

   Temperature characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.temperature.TemperatureCharacteristic
   src.bluetooth_sig.gatt.characteristics.temperature.TemperatureValues


Module Contents
---------------

.. py:class:: TemperatureCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Temperature characteristic (0x2A6E).

   org.bluetooth.characteristic.temperature

   Temperature measurement characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


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



.. py:class:: TemperatureValues

   Special values for Temperature characteristic per Bluetooth SIG specification.


   .. py:attribute:: VALUE_UNKNOWN
      :value: -32768



