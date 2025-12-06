src.bluetooth_sig.gatt.services.device_information
==================================================

.. py:module:: src.bluetooth_sig.gatt.services.device_information

.. autoapi-nested-parse::

   Device Information Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.device_information.DeviceInformationService


Module Contents
---------------

.. py:class:: DeviceInformationService(info: src.bluetooth_sig.types.ServiceInfo | None = None, validation: ServiceValidationConfig | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Device Information Service implementation.

   Contains characteristics that expose device information:
   - Manufacturer Name String - Required
   - Model Number String - Optional
   - Serial Number String - Optional
   - Hardware Revision String - Optional
   - Firmware Revision String - Optional
   - Software Revision String - Optional

   Initialize service with structured configuration.

   :param info: Complete service information (optional for SIG services)
   :param validation: Validation constraints configuration (optional)


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


