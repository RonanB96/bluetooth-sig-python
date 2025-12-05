src.bluetooth_sig.gatt.services.battery_service
===============================================

.. py:module:: src.bluetooth_sig.gatt.services.battery_service

.. autoapi-nested-parse::

   Battery Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.battery_service.BatteryService


Module Contents
---------------

.. py:class:: BatteryService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Battery Service implementation.

   Contains characteristics related to battery information:
   - Battery Level - Required
   - Battery Level Status - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


