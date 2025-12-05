src.bluetooth_sig.gatt.characteristics.voltage
==============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.voltage

.. autoapi-nested-parse::

   Voltage characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.voltage.VoltageCharacteristic


Module Contents
---------------

.. py:class:: VoltageCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Voltage characteristic (0x2B18).

   org.bluetooth.characteristic.voltage

   Voltage characteristic.

   Measures voltage with 1/64 V resolution.


   .. py:attribute:: resolution
      :type:  float
      :value: 0.015625



   .. py:attribute:: max_value
      :type:  float
      :value: 1023.984375



