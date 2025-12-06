src.bluetooth_sig.gatt.services.link_loss
=========================================

.. py:module:: src.bluetooth_sig.gatt.services.link_loss

.. autoapi-nested-parse::

   Link Loss Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.link_loss.LinkLossService


Module Contents
---------------

.. py:class:: LinkLossService(info: src.bluetooth_sig.types.ServiceInfo | None = None, validation: ServiceValidationConfig | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Link Loss Service implementation.

   Defines behaviour when a link is lost between two devices.

   Contains characteristics related to link loss alerts:
   - Alert Level - Required

   Initialize service with structured configuration.

   :param info: Complete service information (optional for SIG services)
   :param validation: Validation constraints configuration (optional)


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


