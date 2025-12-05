src.bluetooth_sig.gatt.characteristics.alert_notification_control_point
=======================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.alert_notification_control_point

.. autoapi-nested-parse::

   Alert Notification Control Point characteristic (0x2A44) implementation.

   Control point for enabling/disabling alert notifications and triggering immediate notifications.
   Used by Alert Notification Service (0x1811).

   Based on Bluetooth SIG GATT Specification:
   - Alert Notification Control Point: 2 bytes (Command ID + Category ID)



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.alert_notification_control_point.AlertNotificationControlPointData
   src.bluetooth_sig.gatt.characteristics.alert_notification_control_point.AlertNotificationControlPointCharacteristic


Module Contents
---------------

.. py:class:: AlertNotificationControlPointData

   Bases: :py:obj:`msgspec.Struct`


   Alert Notification Control Point characteristic data structure.


   .. py:attribute:: command_id
      :type:  src.bluetooth_sig.types.AlertNotificationCommandID


   .. py:attribute:: category_id
      :type:  src.bluetooth_sig.types.AlertCategoryID


.. py:class:: AlertNotificationControlPointCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Alert Notification Control Point characteristic (0x2A44).

   Control point for enabling/disabling notifications and requesting immediate alerts.

   Structure (2 bytes):
   - Command ID: uint8 (0=Enable New Alert, 1=Enable Unread Status, etc.)
   - Category ID: uint8 (0=Simple Alert, 1=Email, etc. - target category for command)

   Commands:
   - 0: Enable New Incoming Alert Notification
   - 1: Enable Unread Category Status Notification
   - 2: Disable New Incoming Alert Notification
   - 3: Disable Unread Category Status Notification
   - 4: Notify New Incoming Alert immediately
   - 5: Notify Unread Category Status immediately

   Used by Alert Notification Service (0x1811).


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> AlertNotificationControlPointData

      Decode Alert Notification Control Point data from bytes.

      :param data: Raw characteristic data (2 bytes)
      :param ctx: Optional characteristic context

      :returns: AlertNotificationControlPointData with all fields

      :raises ValueError: If data is insufficient or contains invalid values



   .. py:method:: encode_value(data: AlertNotificationControlPointData) -> bytearray

      Encode Alert Notification Control Point data to bytes.

      :param data: AlertNotificationControlPointData to encode

      :returns: Encoded alert notification control point (2 bytes)

      :raises ValueError: If data contains invalid values



