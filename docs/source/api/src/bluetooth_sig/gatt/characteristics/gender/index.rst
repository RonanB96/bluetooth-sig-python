src.bluetooth_sig.gatt.characteristics.gender
=============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.gender

.. autoapi-nested-parse::

   Gender characteristic (0x2A8C).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.gender.Gender
   src.bluetooth_sig.gatt.characteristics.gender.GenderCharacteristic


Module Contents
---------------

.. py:class:: Gender

   Bases: :py:obj:`enum.IntEnum`


   Gender enumeration.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: FEMALE
      :value: 1



   .. py:attribute:: MALE
      :value: 0



   .. py:attribute:: UNSPECIFIED
      :value: 2



.. py:class:: GenderCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Gender characteristic (0x2A8C).

   org.bluetooth.characteristic.gender

   The Gender characteristic is used to represent the gender of a user.


   .. py:method:: decode_value(data: bytearray, ctx: bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> Gender

      Decode gender from raw bytes.

      :param data: Raw bytes from BLE characteristic (1 byte)
      :param ctx: Optional context for parsing

      :returns: Gender enum value

      :raises ValueError: If data length is not exactly 1 byte or value is invalid



   .. py:method:: encode_value(data: Gender) -> bytearray

      Encode gender to raw bytes.

      :param data: Gender enum value

      :returns: Encoded bytes
      :rtype: bytearray



