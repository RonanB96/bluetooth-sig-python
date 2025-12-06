src.bluetooth_sig.gatt.services.pulse_oximeter_service
======================================================

.. py:module:: src.bluetooth_sig.gatt.services.pulse_oximeter_service

.. autoapi-nested-parse::

   Pulse Oximeter Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.pulse_oximeter_service.PulseOximeterService


Module Contents
---------------

.. py:class:: PulseOximeterService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Pulse Oximeter Service implementation.

   Contains characteristics related to pulse oximetry:
   - PLX Spot-Check Measurement - Optional
   - PLX Continuous Measurement - Optional
   - PLX Features - Mandatory


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


