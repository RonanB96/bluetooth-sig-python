src.bluetooth_sig.gatt.characteristics.ringer_setting
=====================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.ringer_setting

.. autoapi-nested-parse::

   Ringer Setting characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.ringer_setting.RingerSetting
   src.bluetooth_sig.gatt.characteristics.ringer_setting.RingerSettingData
   src.bluetooth_sig.gatt.characteristics.ringer_setting.RingerSettingCharacteristic


Module Contents
---------------

.. py:class:: RingerSetting

   Bases: :py:obj:`enum.IntEnum`


   Ringer Setting enumeration values.


   .. py:attribute:: RINGER_SILENT
      :value: 0



   .. py:attribute:: RINGER_NORMAL
      :value: 1



.. py:class:: RingerSettingData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Ringer Setting characteristic.


   .. py:attribute:: setting
      :type:  RingerSetting


.. py:class:: RingerSettingCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Ringer Setting characteristic (0x2A41).

   org.bluetooth.characteristic.ringer_setting

   The Ringer Setting characteristic defines the Setting of the Ringer.
   Value 0: Ringer Silent
   Value 1: Ringer Normal
   Values 2-255: Reserved for future use


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> RingerSettingData

      Parse ringer setting data according to Bluetooth specification.

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext (unused)

      :returns: RingerSettingData containing parsed ringer setting.

      :raises ValueError: If data format is invalid.



   .. py:method:: encode_value(data: RingerSettingData) -> bytearray

      Encode RingerSettingData back to bytes.

      :param data: RingerSettingData instance to encode

      :returns: Encoded bytes representing the ringer setting



