src.bluetooth_sig.gatt.characteristics.pollen_concentration
===========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.pollen_concentration

.. autoapi-nested-parse::

   Pollen Concentration characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.pollen_concentration.PollenConcentrationCharacteristic


Module Contents
---------------

.. py:class:: PollenConcentrationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Pollen concentration measurement characteristic (0x2A75).

   Uses uint24 (3 bytes) format as per SIG specification.
   Unit: grains/m³ (count per cubic meter)


   .. py:attribute:: resolution
      :type:  float
      :value: 1.0



