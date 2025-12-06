src.bluetooth_sig.gatt.characteristics.sedentary_interval_notification
======================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.sedentary_interval_notification

.. autoapi-nested-parse::

   Sedentary Interval Notification characteristic (0x2B4F).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.sedentary_interval_notification.SedentaryIntervalNotificationCharacteristic


Module Contents
---------------

.. py:class:: SedentaryIntervalNotificationCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Sedentary Interval Notification characteristic (0x2B4F).

   org.bluetooth.characteristic.sedentary_interval_notification

   Sedentary Interval Notification characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


