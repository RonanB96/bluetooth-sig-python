src.bluetooth_sig.gatt.services.cycling_speed_and_cadence
=========================================================

.. py:module:: src.bluetooth_sig.gatt.services.cycling_speed_and_cadence

.. autoapi-nested-parse::

   Cycling Speed and Cadence Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.cycling_speed_and_cadence.CyclingSpeedAndCadenceService


Module Contents
---------------

.. py:class:: CyclingSpeedAndCadenceService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Cycling Speed and Cadence Service implementation (0x1816).

   Used for cycling sensors that measure wheel and crank revolutions.
   Contains the CSC Measurement characteristic for cycling metrics.


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


