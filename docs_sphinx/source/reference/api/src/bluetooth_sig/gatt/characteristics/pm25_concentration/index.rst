src.bluetooth_sig.gatt.characteristics.pm25_concentration
=========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.pm25_concentration

.. autoapi-nested-parse::

   PM2.5 Concentration characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.pm25_concentration.PM25ConcentrationCharacteristic


Module Contents
---------------

.. py:class:: PM25ConcentrationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   PM2.5 particulate matter concentration characteristic (0x2BD6).

   Represents particulate matter PM2.5 concentration in micrograms per
   cubic meter with a resolution of 1 μg/m³.


   .. py:attribute:: resolution
      :type:  float
      :value: 1.0



   .. py:attribute:: max_value
      :type:  float
      :value: 65533.0



