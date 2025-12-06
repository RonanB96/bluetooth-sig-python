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

.. py:class:: CyclingSpeedAndCadenceService(info: src.bluetooth_sig.types.ServiceInfo | None = None, validation: ServiceValidationConfig | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Cycling Speed and Cadence Service implementation (0x1816).

   Used for cycling sensors that measure wheel and crank revolutions.
   Contains the CSC Measurement characteristic for cycling metrics.

   Initialize service with structured configuration.

   :param info: Complete service information (optional for SIG services)
   :param validation: Validation constraints configuration (optional)


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


