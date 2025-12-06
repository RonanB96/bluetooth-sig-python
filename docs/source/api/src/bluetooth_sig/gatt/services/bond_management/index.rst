src.bluetooth_sig.gatt.services.bond_management
===============================================

.. py:module:: src.bluetooth_sig.gatt.services.bond_management

.. autoapi-nested-parse::

   Bond Management Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.bond_management.BondManagementService


Module Contents
---------------

.. py:class:: BondManagementService(info: src.bluetooth_sig.types.ServiceInfo | None = None, validation: ServiceValidationConfig | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Bond Management Service implementation.

   Contains characteristics for managing Bluetooth bonds:
   - Bond Management Feature - Required
   - Bond Management Control Point - Required

   Initialize service with structured configuration.

   :param info: Complete service information (optional for SIG services)
   :param validation: Validation constraints configuration (optional)


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


