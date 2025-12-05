src.bluetooth_sig.gatt.characteristics.nitrogen_dioxide_concentration
=====================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.nitrogen_dioxide_concentration

.. autoapi-nested-parse::

   Nitrogen Dioxide Concentration characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.nitrogen_dioxide_concentration.NitrogenDioxideConcentrationCharacteristic


Module Contents
---------------

.. py:class:: NitrogenDioxideConcentrationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Nitrogen dioxide concentration measurement characteristic (0x2BD2).

   Represents nitrogen dioxide (NO2) concentration in parts per billion
   (ppb) with a resolution of 1 ppb.


   .. py:attribute:: resolution
      :type:  float
      :value: 1.0



   .. py:attribute:: max_value
      :type:  float
      :value: 65533.0



