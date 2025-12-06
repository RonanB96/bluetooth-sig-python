src.bluetooth_sig.gatt.characteristics.apparent_energy_32
=========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.apparent_energy_32

.. autoapi-nested-parse::

   Apparent Energy 32 characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.apparent_energy_32.ApparentEnergy32Characteristic
   src.bluetooth_sig.gatt.characteristics.apparent_energy_32.ApparentEnergy32Values


Module Contents
---------------

.. py:class:: ApparentEnergy32Characteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Apparent Energy 32 characteristic (0x2B89).

   org.bluetooth.characteristic.apparent_energy_32

   The Apparent Energy 32 characteristic is used to represent the integral of Apparent Power over a time interval.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> float | None

      Decode apparent energy 32 characteristic.

      Decodes a 32-bit unsigned integer representing apparent energy in 0.001 kVAh increments
      per Bluetooth SIG Apparent Energy 32 characteristic specification.

      :param data: Raw bytes from BLE characteristic (exactly 4 bytes, little-endian)
      :param ctx: Optional context for parsing (device info, flags, etc.)

      :returns: Apparent energy in kilovolt ampere hours, or None if value is not valid or unknown

      :raises InsufficientDataError: If data is not exactly 4 bytes



   .. py:method:: encode_value(data: float) -> bytearray

      Encode apparent energy value.



   .. py:attribute:: expected_length
      :value: 4



.. py:class:: ApparentEnergy32Values

   Special values for Apparent Energy 32 characteristic per Bluetooth SIG specification.


   .. py:attribute:: VALUE_NOT_VALID
      :value: 4294967294



   .. py:attribute:: VALUE_UNKNOWN
      :value: 4294967295



