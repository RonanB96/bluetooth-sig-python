src.bluetooth_sig.gatt.characteristics.unread_alert_status
==========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.unread_alert_status

.. autoapi-nested-parse::

   Unread Alert Status characteristic (0x2A45) implementation.

   Represents the number of unread alerts in a specific category.
   Used by Alert Notification Service (0x1811).

   Based on Bluetooth SIG GATT Specification:
   - Unread Alert Status: 2 bytes (Category ID + Unread Count)



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.unread_alert_status.UnreadAlertStatusCharacteristic
   src.bluetooth_sig.gatt.characteristics.unread_alert_status.UnreadAlertStatusData


Module Contents
---------------

.. py:class:: UnreadAlertStatusCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Unread Alert Status characteristic (0x2A45).

   Represents the number of unread alerts in a specific category.

   Structure (2 bytes):
   - Category ID: uint8 (0=Simple Alert, 1=Email, etc.)
   - Unread Count: uint8 (0-254, 255 means more than 254 unread alerts)

   Used by Alert Notification Service (0x1811).

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> UnreadAlertStatusData

      Decode Unread Alert Status data from bytes.

      :param data: Raw characteristic data (2 bytes)
      :param ctx: Optional characteristic context

      :returns: UnreadAlertStatusData with all fields

      :raises ValueError: If data is insufficient or contains invalid values



   .. py:method:: encode_value(data: UnreadAlertStatusData) -> bytearray

      Encode Unread Alert Status data to bytes.

      :param data: UnreadAlertStatusData to encode

      :returns: Encoded unread alert status (2 bytes)

      :raises ValueError: If data contains invalid values



.. py:class:: UnreadAlertStatusData

   Bases: :py:obj:`msgspec.Struct`


   Unread Alert Status characteristic data structure.


   .. py:attribute:: category_id
      :type:  src.bluetooth_sig.types.AlertCategoryID


   .. py:attribute:: unread_count
      :type:  int


