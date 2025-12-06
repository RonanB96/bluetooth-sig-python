src.bluetooth_sig.gatt.services.generic_access
==============================================

.. py:module:: src.bluetooth_sig.gatt.services.generic_access

.. autoapi-nested-parse::

   Generic Access Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.generic_access.GenericAccessService


Module Contents
---------------

.. py:class:: GenericAccessService(info: src.bluetooth_sig.types.ServiceInfo | None = None, validation: ServiceValidationConfig | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Generic Access Service implementation.

   Contains characteristics that expose basic device access information:
   - Device Name - Required
   - Appearance - Optional

   Initialize service with structured configuration.

   :param info: Complete service information (optional for SIG services)
   :param validation: Validation constraints configuration (optional)


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


