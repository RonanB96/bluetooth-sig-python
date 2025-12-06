src.bluetooth_sig.gatt.services.health_thermometer
==================================================

.. py:module:: src.bluetooth_sig.gatt.services.health_thermometer

.. autoapi-nested-parse::

   Health Thermometer Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.health_thermometer.HealthThermometerService


Module Contents
---------------

.. py:class:: HealthThermometerService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Health Thermometer Service implementation (0x1809).

   Used for medical temperature measurement devices. Contains the
   Temperature Measurement characteristic for medical-grade temperature
   readings.


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


