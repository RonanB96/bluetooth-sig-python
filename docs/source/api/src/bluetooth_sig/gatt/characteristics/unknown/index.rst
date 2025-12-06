src.bluetooth_sig.gatt.characteristics.unknown
==============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.unknown

.. autoapi-nested-parse::

   Unknown characteristic implementation for non-SIG characteristics.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.unknown.UnknownCharacteristic


Module Contents
---------------

.. py:class:: UnknownCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Generic characteristic implementation for unknown/non-SIG characteristics.

   This class provides basic functionality for characteristics that are not
   defined in the Bluetooth SIG specification. It stores raw data without
   attempting to parse it into structured types.

   Initialize an unknown characteristic.

   :param info: CharacteristicInfo object with UUID, name, unit, value_type
   :param properties: Runtime BLE properties discovered from device (optional)

   :raises ValueError: If UUID is invalid


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> bytes

      Return raw bytes for unknown characteristics.

      :param data: Raw bytes from the characteristic read
      :param ctx: Optional context (ignored)

      :returns: Raw bytes as-is



   .. py:method:: encode_value(data: Any) -> bytearray

      Encode data to bytes for unknown characteristics.

      :param data: Data to encode (must be bytes or bytearray)

      :returns: Encoded bytes

      :raises ValueError: If data is not bytes/bytearray



