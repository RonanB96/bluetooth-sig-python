src.bluetooth_sig.gatt.characteristics.high_voltage
===================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.high_voltage

.. autoapi-nested-parse::

   High Voltage characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.high_voltage.HighVoltageCharacteristic


Module Contents
---------------

.. py:class:: HighVoltageCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   High Voltage characteristic (0x2BE0).

   org.bluetooth.characteristic.high_voltage

   High Voltage characteristic.

   Measures high voltage systems using uint24 (3 bytes) format.


   .. py:attribute:: resolution
      :type:  float
      :value: 1.0



