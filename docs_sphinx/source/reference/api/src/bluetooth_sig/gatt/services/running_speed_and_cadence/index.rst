src.bluetooth_sig.gatt.services.running_speed_and_cadence
=========================================================

.. py:module:: src.bluetooth_sig.gatt.services.running_speed_and_cadence

.. autoapi-nested-parse::

   Running Speed and Cadence Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.running_speed_and_cadence.RunningSpeedAndCadenceService


Module Contents
---------------

.. py:class:: RunningSpeedAndCadenceService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Running Speed and Cadence Service implementation (0x1814).

   Used for running sensors that measure speed, cadence, stride length,
   and distance. Contains the RSC Measurement characteristic for
   running metrics.


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


