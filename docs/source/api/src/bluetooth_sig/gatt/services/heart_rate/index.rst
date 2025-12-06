src.bluetooth_sig.gatt.services.heart_rate
==========================================

.. py:module:: src.bluetooth_sig.gatt.services.heart_rate

.. autoapi-nested-parse::

   Heart Rate Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.heart_rate.HeartRateService


Module Contents
---------------

.. py:class:: HeartRateService(info: src.bluetooth_sig.types.ServiceInfo | None = None, validation: ServiceValidationConfig | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Heart Rate Service implementation (0x180D).

   Used for heart rate monitoring devices. Contains the Heart Rate
   Measurement characteristic for heart rate data with optional RR-
   intervals and energy expenditure.

   Initialize service with structured configuration.

   :param info: Complete service information (optional for SIG services)
   :param validation: Validation constraints configuration (optional)


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


