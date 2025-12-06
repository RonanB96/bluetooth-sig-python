src.bluetooth_sig.gatt.services.alert_notification
==================================================

.. py:module:: src.bluetooth_sig.gatt.services.alert_notification

.. autoapi-nested-parse::

   Alert Notification Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.alert_notification.AlertNotificationService


Module Contents
---------------

.. py:class:: AlertNotificationService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Alert Notification Service implementation.

   Exposes alert information from a device to a peer device.

   Contains characteristics related to alert notifications:
   - Supported New Alert Category - Required
   - New Alert - Optional
   - Supported Unread Alert Category - Required
   - Unread Alert Status - Optional
   - Alert Notification Control Point - Required


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


