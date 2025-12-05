src.bluetooth_sig.gatt.services.glucose
=======================================

.. py:module:: src.bluetooth_sig.gatt.services.glucose

.. autoapi-nested-parse::

   Glucose Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.glucose.GlucoseService


Module Contents
---------------

.. py:class:: GlucoseService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Glucose Service implementation (0x1808).

   Used for glucose monitoring devices including continuous glucose
   monitors (CGMs) and traditional glucose meters. Provides
   comprehensive glucose measurement data with context and device
   capabilities.


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


