src.bluetooth_sig.gatt.services.generic_attribute
=================================================

.. py:module:: src.bluetooth_sig.gatt.services.generic_attribute

.. autoapi-nested-parse::

   Generic Attribute Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.generic_attribute.GenericAttributeService


Module Contents
---------------

.. py:class:: GenericAttributeService(info: src.bluetooth_sig.types.ServiceInfo | None = None, validation: ServiceValidationConfig | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Generic Attribute Service implementation.

   The GATT Service contains information about the GATT database and is
   primarily used for service discovery and attribute access.

   This service typically contains:
   - Service Changed characteristic (optional)

   Initialize service with structured configuration.

   :param info: Complete service information (optional for SIG services)
   :param validation: Validation constraints configuration (optional)


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


