src.bluetooth_sig.gatt.characteristics.illuminance
==================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.illuminance

.. autoapi-nested-parse::

   Illuminance characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.illuminance.IlluminanceValues
   src.bluetooth_sig.gatt.characteristics.illuminance.IlluminanceCharacteristic


Module Contents
---------------

.. py:class:: IlluminanceValues

   Special values for Illuminance characteristic per Bluetooth SIG specification.


   .. py:attribute:: VALUE_UNKNOWN
      :value: 16777215



.. py:class:: IlluminanceCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Illuminance characteristic (0x2AFB).

   Measures light intensity in lux (lumens per square meter).
   Uses uint24 (3 bytes) with 0.01 lux resolution.


   .. py:attribute:: resolution
      :type:  float
      :value: 0.01



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> float | None

      Decode illuminance characteristic.

      Decodes a 24-bit unsigned integer representing illuminance in 0.01 lux increments
      per Bluetooth SIG Illuminance characteristic specification.

      :param data: Raw bytes from BLE characteristic (exactly 3 bytes, little-endian)
      :param ctx: Optional context for parsing (device info, flags, etc.)

      :returns: Illuminance in lux, or None if value is unknown (0xFFFFFF)

      :raises InsufficientDataError: If data is not exactly 3 bytes



   .. py:method:: encode_value(data: float) -> bytearray

      Encode illuminance value.



