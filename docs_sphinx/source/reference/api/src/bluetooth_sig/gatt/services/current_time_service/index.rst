src.bluetooth_sig.gatt.services.current_time_service
====================================================

.. py:module:: src.bluetooth_sig.gatt.services.current_time_service

.. autoapi-nested-parse::

   Current Time Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.current_time_service.CurrentTimeService


Module Contents
---------------

.. py:class:: CurrentTimeService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Current Time Service implementation.

   Exposes the current date and time with additional information.

   Contains characteristics related to time:
   - Current Time - Required
   - Local Time Information - Optional
   - Reference Time Information - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


