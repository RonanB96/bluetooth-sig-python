src.bluetooth_sig.gatt.characteristics.humidity
===============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.humidity

.. autoapi-nested-parse::

   Humidity characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.humidity.HumidityValues
   src.bluetooth_sig.gatt.characteristics.humidity.HumidityCharacteristic


Module Contents
---------------

.. py:class:: HumidityValues

   Special values for Humidity characteristic per Bluetooth SIG specification.


   .. py:attribute:: VALUE_UNKNOWN
      :value: 65535



.. py:class:: HumidityCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Humidity characteristic (0x2A6F).

   org.bluetooth.characteristic.humidity

   Humidity measurement characteristic.


   .. py:attribute:: resolution
      :type:  float
      :value: 0.01



   .. py:attribute:: max_value
      :type:  int | float | None
      :value: 100



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



