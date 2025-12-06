src.bluetooth_sig.gatt.characteristics.methane_concentration
============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.methane_concentration

.. autoapi-nested-parse::

   Methane Concentration characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.methane_concentration.MethaneConcentrationCharacteristic


Module Contents
---------------

.. py:class:: MethaneConcentrationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Methane concentration measurement characteristic (0x2BD1).

   Represents methane concentration in parts per million (ppm) with a
   resolution of 1 ppm.


   .. py:attribute:: max_value
      :type:  float
      :value: 65533.0



   .. py:attribute:: resolution
      :type:  float
      :value: 1.0



