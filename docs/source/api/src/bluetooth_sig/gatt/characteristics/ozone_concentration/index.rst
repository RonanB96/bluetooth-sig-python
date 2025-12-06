src.bluetooth_sig.gatt.characteristics.ozone_concentration
==========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.ozone_concentration

.. autoapi-nested-parse::

   Ozone Concentration characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.ozone_concentration.OzoneConcentrationCharacteristic


Module Contents
---------------

.. py:class:: OzoneConcentrationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Ozone concentration measurement characteristic (0x2BD4).

   Represents ozone concentration in parts per billion (ppb) with a
   resolution of 1 ppb.


   .. py:attribute:: max_value
      :type:  float
      :value: 65533.0



   .. py:attribute:: resolution
      :type:  float
      :value: 1.0



