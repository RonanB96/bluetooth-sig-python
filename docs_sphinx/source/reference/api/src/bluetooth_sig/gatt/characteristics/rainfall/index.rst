src.bluetooth_sig.gatt.characteristics.rainfall
===============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.rainfall

.. autoapi-nested-parse::

   Rainfall characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.rainfall.RainfallCharacteristic


Module Contents
---------------

.. py:class:: RainfallCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Rainfall characteristic (0x2A78).

   org.bluetooth.characteristic.rainfall

   Rainfall characteristic.

   Represents the amount of rain that has fallen in millimeters. Uses
   uint16 with 1 mm resolution (1:1 scaling).


   .. py:attribute:: resolution
      :type:  float
      :value: 1.0



