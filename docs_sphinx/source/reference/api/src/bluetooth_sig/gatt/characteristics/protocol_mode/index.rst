src.bluetooth_sig.gatt.characteristics.protocol_mode
====================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.protocol_mode

.. autoapi-nested-parse::

   Protocol Mode characteristic implementation.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.protocol_mode.PROTOCOL_MODE_DATA_LENGTH


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.protocol_mode.ProtocolMode
   src.bluetooth_sig.gatt.characteristics.protocol_mode.ProtocolModeCharacteristic


Module Contents
---------------

.. py:data:: PROTOCOL_MODE_DATA_LENGTH
   :value: 1


.. py:class:: ProtocolMode

   Bases: :py:obj:`enum.IntEnum`


   Protocol Mode values.


   .. py:attribute:: BOOT_PROTOCOL
      :value: 0



   .. py:attribute:: REPORT_PROTOCOL
      :value: 1



.. py:class:: ProtocolModeCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Protocol Mode characteristic (0x2A4E).

   org.bluetooth.characteristic.protocol_mode

   Protocol Mode characteristic.


   .. py:attribute:: expected_length
      :value: 1



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> ProtocolMode

      Parse protocol mode data.

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional context.

      :returns: Protocol mode.



   .. py:method:: encode_value(data: ProtocolMode) -> bytearray

      Encode protocol mode back to bytes.

      :param data: Protocol mode to encode

      :returns: Encoded bytes



