src.bluetooth_sig.gatt.characteristics.handedness
=================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.handedness

.. autoapi-nested-parse::

   Handedness characteristic (0x2B4A).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.handedness.Handedness
   src.bluetooth_sig.gatt.characteristics.handedness.HandednessCharacteristic


Module Contents
---------------

.. py:class:: Handedness

   Bases: :py:obj:`enum.IntEnum`


   Handedness enumeration.


   .. py:attribute:: LEFT_HANDED
      :value: 0



   .. py:attribute:: RIGHT_HANDED
      :value: 1



   .. py:attribute:: AMBIDEXTROUS
      :value: 2



   .. py:attribute:: UNSPECIFIED
      :value: 3



.. py:class:: HandednessCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Handedness characteristic (0x2B4A).

   org.bluetooth.characteristic.handedness

   The Handedness characteristic is used to represent the handedness of a user.


   .. py:method:: decode_value(data: bytearray, ctx: bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> Handedness

      Decode handedness from raw bytes.

      :param data: Raw bytes from BLE characteristic (1 byte)
      :param ctx: Optional context for parsing

      :returns: Handedness enum value

      :raises ValueError: If data length is not exactly 1 byte or value is invalid



   .. py:method:: encode_value(data: Handedness) -> bytearray

      Encode handedness to raw bytes.

      :param data: Handedness enum value

      :returns: Encoded bytes
      :rtype: bytearray



