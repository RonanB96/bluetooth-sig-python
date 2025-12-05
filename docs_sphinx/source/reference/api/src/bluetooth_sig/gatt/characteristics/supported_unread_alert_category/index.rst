src.bluetooth_sig.gatt.characteristics.supported_unread_alert_category
======================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.supported_unread_alert_category

.. autoapi-nested-parse::

   Supported Unread Alert Category characteristic (0x2A48) implementation.

   Represents which alert categories the server supports for unread alerts.
   Used by Alert Notification Service (0x1811).

   Based on Bluetooth SIG GATT Specification:
   - Supported Unread Alert Category: 2 bytes (16-bit Category ID Bit Mask)



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.supported_unread_alert_category.SupportedUnreadAlertCategoryCharacteristic


Module Contents
---------------

.. py:class:: SupportedUnreadAlertCategoryCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Supported Unread Alert Category characteristic (0x2A48).

   Represents which alert categories the server supports for unread alerts
   using a 16-bit bitmask.

   Structure (2 bytes):
   - Category ID Bit Mask: uint16 (bit 0=Simple Alert, bit 1=Email, etc.)
     Bits 10-15 reserved for future use

   Used by Alert Notification Service (0x1811).


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> src.bluetooth_sig.types.AlertCategoryBitMask

      Decode Supported Unread Alert Category data from bytes.

      :param data: Raw characteristic data (2 bytes)
      :param ctx: Optional characteristic context

      :returns: AlertCategoryBitMask flags

      :raises ValueError: If data is insufficient



   .. py:method:: encode_value(data: src.bluetooth_sig.types.AlertCategoryBitMask | int) -> bytearray

      Encode Supported Unread Alert Category data to bytes.

      :param data: AlertCategoryBitMask or int value

      :returns: Encoded supported unread alert category (2 bytes)



