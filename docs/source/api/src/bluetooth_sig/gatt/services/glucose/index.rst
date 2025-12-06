src.bluetooth_sig.gatt.services.glucose
=======================================

.. py:module:: src.bluetooth_sig.gatt.services.glucose

.. autoapi-nested-parse::

   Glucose Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.glucose.GlucoseService


Module Contents
---------------

.. py:class:: GlucoseService(info: src.bluetooth_sig.types.ServiceInfo | None = None, validation: ServiceValidationConfig | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Glucose Service implementation (0x1808).

   Used for glucose monitoring devices including continuous glucose
   monitors (CGMs) and traditional glucose meters. Provides
   comprehensive glucose measurement data with context and device
   capabilities.

   Initialize service with structured configuration.

   :param info: Complete service information (optional for SIG services)
   :param validation: Validation constraints configuration (optional)


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


