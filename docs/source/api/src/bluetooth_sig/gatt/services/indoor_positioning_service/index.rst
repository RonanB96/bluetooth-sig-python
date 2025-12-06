src.bluetooth_sig.gatt.services.indoor_positioning_service
==========================================================

.. py:module:: src.bluetooth_sig.gatt.services.indoor_positioning_service

.. autoapi-nested-parse::

   Indoor Positioning Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.indoor_positioning_service.IndoorPositioningService


Module Contents
---------------

.. py:class:: IndoorPositioningService(info: src.bluetooth_sig.types.ServiceInfo | None = None, validation: ServiceValidationConfig | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Indoor Positioning Service implementation.

   Contains characteristics related to indoor positioning:
   - Latitude - Mandatory
   - Longitude - Mandatory
   - Local North Coordinate - Optional
   - Local East Coordinate - Optional
   - Floor Number - Optional
   - Altitude - Optional
   - Uncertainty - Optional
   - Location Name - Optional
   - Indoor Positioning Configuration - Optional

   Initialize service with structured configuration.

   :param info: Complete service information (optional for SIG services)
   :param validation: Validation constraints configuration (optional)


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


