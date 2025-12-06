src.bluetooth_sig.gatt.characteristics.elevation
================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.elevation

.. autoapi-nested-parse::

   Elevation characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.elevation.ElevationCharacteristic


Module Contents
---------------

.. py:class:: ElevationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Elevation characteristic (0x2A6C).

   org.bluetooth.characteristic.elevation

   Elevation characteristic.

   Represents the elevation relative to sea level unless otherwise
   specified in the service.

   Format: sint24 (3 bytes) with 0.01 meter resolution.


   .. py:attribute:: resolution
      :type:  float
      :value: 0.01



