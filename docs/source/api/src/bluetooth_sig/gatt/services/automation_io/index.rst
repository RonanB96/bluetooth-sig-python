src.bluetooth_sig.gatt.services.automation_io
=============================================

.. py:module:: src.bluetooth_sig.gatt.services.automation_io

.. autoapi-nested-parse::

   Automation IO Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.automation_io.AutomationIOService


Module Contents
---------------

.. py:class:: AutomationIOService(info: src.bluetooth_sig.types.ServiceInfo | None = None, validation: ServiceValidationConfig | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Automation IO Service implementation.

   Contains characteristics related to electrical power monitoring and automation:
   - Electric Current - Optional
   - Voltage - Optional
   - Average Current - Optional
   - Average Voltage - Optional
   - Electric Current Range - Optional
   - Electric Current Specification - Optional
   - Electric Current Statistics - Optional
   - Voltage Specification - Optional
   - Voltage Statistics - Optional
   - High Voltage - Optional
   - Voltage Frequency - Optional
   - Supported Power Range - Optional
   - Tx Power Level - Optional

   Initialize service with structured configuration.

   :param info: Complete service information (optional for SIG services)
   :param validation: Validation constraints configuration (optional)


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


