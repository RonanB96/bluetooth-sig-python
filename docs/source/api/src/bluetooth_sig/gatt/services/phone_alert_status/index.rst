src.bluetooth_sig.gatt.services.phone_alert_status
==================================================

.. py:module:: src.bluetooth_sig.gatt.services.phone_alert_status

.. autoapi-nested-parse::

   Phone Alert Status Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.phone_alert_status.PhoneAlertStatusService


Module Contents
---------------

.. py:class:: PhoneAlertStatusService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Phone Alert Status Service implementation.

   Contains characteristics related to phone alert status:
   - Alert Status - Required
   - Ringer Setting - Required
   - Ringer Control Point - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


