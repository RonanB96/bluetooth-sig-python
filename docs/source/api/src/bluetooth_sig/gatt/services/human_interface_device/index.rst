src.bluetooth_sig.gatt.services.human_interface_device
======================================================

.. py:module:: src.bluetooth_sig.gatt.services.human_interface_device

.. autoapi-nested-parse::

   Human Interface Device Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.human_interface_device.HumanInterfaceDeviceService


Module Contents
---------------

.. py:class:: HumanInterfaceDeviceService(info: src.bluetooth_sig.types.ServiceInfo | None = None, validation: ServiceValidationConfig | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Human Interface Device Service implementation.

   Contains characteristics related to HID:
   - HID Information - Required
   - HID Control Point - Required
   - Report Map - Required
   - Report - Required
   - Protocol Mode - Required
   - PnP ID - Optional

   Initialize service with structured configuration.

   :param info: Complete service information (optional for SIG services)
   :param validation: Validation constraints configuration (optional)


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


