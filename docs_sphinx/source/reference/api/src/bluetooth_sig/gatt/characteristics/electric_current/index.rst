src.bluetooth_sig.gatt.characteristics.electric_current
=======================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.electric_current

.. autoapi-nested-parse::

   Electric Current characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.electric_current.ElectricCurrentCharacteristic


Module Contents
---------------

.. py:class:: ElectricCurrentCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Electric Current characteristic (0x2AEE).

   org.bluetooth.characteristic.electric_current

   Electric Current characteristic.

   Measures electric current with 0.01 A resolution.


   .. py:attribute:: resolution
      :type:  float
      :value: 0.01



   .. py:attribute:: max_value
      :type:  float
      :value: 655.35



