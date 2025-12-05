src.bluetooth_sig.gatt.characteristics.hid_information
======================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.hid_information

.. autoapi-nested-parse::

   HID Information characteristic implementation.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.hid_information.BCD_HID_MAX
   src.bluetooth_sig.gatt.characteristics.hid_information.COUNTRY_CODE_MAX
   src.bluetooth_sig.gatt.characteristics.hid_information.HID_INFO_DATA_LENGTH


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.hid_information.HidInformationFlags
   src.bluetooth_sig.gatt.characteristics.hid_information.HidInformationData
   src.bluetooth_sig.gatt.characteristics.hid_information.HidInformationCharacteristic


Module Contents
---------------

.. py:data:: BCD_HID_MAX
   :value: 65535


.. py:data:: COUNTRY_CODE_MAX
   :value: 255


.. py:data:: HID_INFO_DATA_LENGTH
   :value: 4


.. py:class:: HidInformationFlags

   Bases: :py:obj:`enum.IntFlag`


   HID Information flags as per Bluetooth HID specification.


   .. py:attribute:: REMOTE_WAKE
      :value: 1



   .. py:attribute:: NORMALLY_CONNECTABLE
      :value: 2



.. py:class:: HidInformationData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from HID Information characteristic.

   .. attribute:: bcd_hid

      HID version in BCD format (uint16)

   .. attribute:: b_country_code

      Country code (uint8)

   .. attribute:: flags

      HID information flags


   .. py:attribute:: bcd_hid
      :type:  int


   .. py:attribute:: b_country_code
      :type:  int


   .. py:attribute:: flags
      :type:  HidInformationFlags


.. py:class:: HidInformationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   HID Information characteristic (0x2A4A).

   org.bluetooth.characteristic.hid_information

   HID Information characteristic.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> HidInformationData

      Parse HID information data.

      Format: bcdHID(2) + bCountryCode(1) + Flags(1)

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional context.

      :returns: HidInformationData containing parsed HID information.



   .. py:method:: encode_value(data: HidInformationData) -> bytearray

      Encode HidInformationData back to bytes.

      :param data: HidInformationData instance to encode

      :returns: Encoded bytes



