src.bluetooth_sig.gatt.services.reference_time_update
=====================================================

.. py:module:: src.bluetooth_sig.gatt.services.reference_time_update

.. autoapi-nested-parse::

   Reference Time Update Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.reference_time_update.ReferenceTimeUpdateService


Module Contents
---------------

.. py:class:: ReferenceTimeUpdateService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Reference Time Update Service implementation.

   Allows clients to request time updates from reference time sources.

   Contains characteristics related to time updates:
   - Time Update Control Point - Required
   - Time Update State - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


