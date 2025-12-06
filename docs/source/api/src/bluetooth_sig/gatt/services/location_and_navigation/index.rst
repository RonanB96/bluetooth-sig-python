src.bluetooth_sig.gatt.services.location_and_navigation
=======================================================

.. py:module:: src.bluetooth_sig.gatt.services.location_and_navigation

.. autoapi-nested-parse::

   Location and Navigation Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.location_and_navigation.LocationAndNavigationService


Module Contents
---------------

.. py:class:: LocationAndNavigationService(info: src.bluetooth_sig.types.ServiceInfo | None = None, validation: ServiceValidationConfig | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Location and Navigation Service implementation.

   Contains characteristics related to location and navigation data:
   - LN Feature - Required
   - Location and Speed - Optional
   - Navigation - Optional
   - Position Quality - Optional
   - LN Control Point - Optional

   Initialize service with structured configuration.

   :param info: Complete service information (optional for SIG services)
   :param validation: Validation constraints configuration (optional)


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


