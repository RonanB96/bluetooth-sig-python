src.bluetooth_sig.gatt.characteristics.alert_category_id_bit_mask
=================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.alert_category_id_bit_mask

.. autoapi-nested-parse::

   Alert Category ID Bit Mask characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.alert_category_id_bit_mask.AlertCategoryIdBitMaskCharacteristic


Module Contents
---------------

.. py:class:: AlertCategoryIdBitMaskCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Alert Category ID Bit Mask characteristic (0x2A42).

   org.bluetooth.characteristic.alert_category_id_bit_mask

   The Alert Category ID Bit Mask characteristic is used to represent
   support for predefined categories of alerts and messages using a bit mask.

   Structure (2 bytes):
   - Category ID Bit Mask: uint16 (bit field where each bit represents support for a category)
     Bit 0: Simple Alert
     Bit 1: Email
     Bit 2: News
     Bit 3: Call
     Bit 4: Missed Call
     Bit 5: SMS/MMS
     Bit 6: Voice Mail
     Bit 7: Schedule
     Bit 8: High Prioritized Alert
     Bit 9: Instant Message
     Bits 10-15: Reserved for Future Use

   Used by Alert Notification Service (0x1811).

   Spec: Bluetooth SIG GATT Specification Supplement, Alert Category ID Bit Mask


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> src.bluetooth_sig.types.AlertCategoryBitMask

      Decode Alert Category ID Bit Mask data from bytes.

      :param data: Raw characteristic data (2 bytes)
      :param ctx: Optional characteristic context

      :returns: AlertCategoryBitMask flags

      :raises ValueError: If data is insufficient



   .. py:method:: encode_value(data: src.bluetooth_sig.types.AlertCategoryBitMask | int) -> bytearray

      Encode Alert Category ID Bit Mask data to bytes.

      :param data: AlertCategoryBitMask or int value

      :returns: Encoded alert category ID bit mask (2 bytes)



