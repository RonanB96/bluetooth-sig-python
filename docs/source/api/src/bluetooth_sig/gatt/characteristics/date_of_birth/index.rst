src.bluetooth_sig.gatt.characteristics.date_of_birth
====================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.date_of_birth

.. autoapi-nested-parse::

   Date of Birth characteristic (0x2A85).



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.date_of_birth.DateOfBirthData


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.date_of_birth.DateOfBirthCharacteristic


Module Contents
---------------

.. py:class:: DateOfBirthCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Date of Birth characteristic (0x2A85).

   org.bluetooth.characteristic.date_of_birth

   Date of Birth characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> DateOfBirthData

      Decode Date of Birth from raw bytes.

      :param data: Raw bytes from BLE characteristic (exactly 4 bytes)
      :param ctx: Optional context for parsing

      :returns: Parsed date of birth
      :rtype: DateOfBirthData



   .. py:method:: encode_value(data: DateOfBirthData) -> bytearray

      Encode Date of Birth to raw bytes.

      :param data: DateOfBirthData to encode

      :returns: Encoded bytes
      :rtype: bytearray



   .. py:attribute:: expected_length
      :value: 4



.. py:data:: DateOfBirthData

