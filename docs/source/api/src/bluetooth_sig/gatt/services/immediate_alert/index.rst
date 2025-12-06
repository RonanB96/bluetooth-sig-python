src.bluetooth_sig.gatt.services.immediate_alert
===============================================

.. py:module:: src.bluetooth_sig.gatt.services.immediate_alert

.. autoapi-nested-parse::

   Immediate Alert Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.immediate_alert.ImmediateAlertService


Module Contents
---------------

.. py:class:: ImmediateAlertService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Immediate Alert Service implementation.

   Exposes a control point to allow a peer device to cause the device to
   immediately alert.

   Contains characteristics related to immediate alerts:
   - Alert Level - Required


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


