src.bluetooth_sig.gatt.services.scan_parameters
===============================================

.. py:module:: src.bluetooth_sig.gatt.services.scan_parameters

.. autoapi-nested-parse::

   Scan Parameters service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.scan_parameters.ScanParametersService


Module Contents
---------------

.. py:class:: ScanParametersService(info: src.bluetooth_sig.types.ServiceInfo | None = None, validation: ServiceValidationConfig | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Scan Parameters service implementation.

   Contains characteristics that control BLE scanning parameters:
   - Scan Interval Window - Required

   Initialize service with structured configuration.

   :param info: Complete service information (optional for SIG services)
   :param validation: Validation constraints configuration (optional)


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


