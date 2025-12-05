src.bluetooth_sig.gatt.characteristics.sulfur_dioxide_concentration
===================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.sulfur_dioxide_concentration

.. autoapi-nested-parse::

   Sulfur Dioxide Concentration characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.sulfur_dioxide_concentration.SulfurDioxideConcentrationCharacteristic


Module Contents
---------------

.. py:class:: SulfurDioxideConcentrationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Sulfur Dioxide Concentration characteristic (0x2BD8).

   org.bluetooth.characteristic.sulfur_dioxide_concentration

   Sulfur dioxide concentration measurement characteristic (0x2BD3).

   Represents sulfur dioxide (SO2) concentration in parts per billion
   (ppb) with a resolution of 1 ppb.


   .. py:attribute:: resolution
      :type:  float
      :value: 1.0



   .. py:attribute:: max_value
      :type:  float
      :value: 65533.0



