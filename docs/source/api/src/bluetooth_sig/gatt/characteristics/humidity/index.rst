src.bluetooth_sig.gatt.characteristics.humidity
===============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.humidity

.. autoapi-nested-parse::

   Humidity characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.humidity.HumidityCharacteristic
   src.bluetooth_sig.gatt.characteristics.humidity.HumidityValues


Module Contents
---------------

.. py:class:: HumidityCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Humidity characteristic (0x2A6F).

   org.bluetooth.characteristic.humidity

   Humidity measurement characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> float | None

      Decode humidity characteristic.

      Decodes a 16-bit unsigned integer representing humidity in 0.01% increments
      per Bluetooth SIG Humidity characteristic specification.

      :param data: Raw bytes from BLE characteristic (exactly 2 bytes, little-endian)
      :param ctx: Optional context for parsing (device info, flags, etc.)

      :returns: Humidity percentage (0.00% to 100.00%), or None if value is unknown (0xFFFF)

      :raises InsufficientDataError: If data is not exactly 2 bytes



   .. py:method:: encode_value(data: float) -> bytearray

      Encode humidity value.



   .. py:attribute:: max_value
      :type:  int | float | None
      :value: 100



   .. py:attribute:: resolution
      :type:  float
      :value: 0.01



.. py:class:: HumidityValues

   Special values for Humidity characteristic per Bluetooth SIG specification.


   .. py:attribute:: VALUE_UNKNOWN
      :value: 65535



