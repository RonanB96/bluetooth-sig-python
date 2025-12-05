src.bluetooth_sig.gatt.characteristics.pm10_concentration
=========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.pm10_concentration

.. autoapi-nested-parse::

   PM10 Concentration characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.pm10_concentration.PM10ConcentrationCharacteristic


Module Contents
---------------

.. py:class:: PM10ConcentrationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   PM10 particulate matter concentration characteristic (0x2BD7).

   Represents particulate matter PM10 concentration in micrograms per
   cubic meter with a resolution of 1 μg/m³.


   .. py:attribute:: resolution
      :type:  float
      :value: 1.0



   .. py:attribute:: max_value
      :type:  float
      :value: 65533.0



