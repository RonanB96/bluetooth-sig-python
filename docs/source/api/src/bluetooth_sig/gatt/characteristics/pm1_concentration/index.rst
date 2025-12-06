src.bluetooth_sig.gatt.characteristics.pm1_concentration
========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.pm1_concentration

.. autoapi-nested-parse::

   PM1 Concentration characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.pm1_concentration.PM1ConcentrationCharacteristic


Module Contents
---------------

.. py:class:: PM1ConcentrationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Particulate Matter - PM1 Concentration characteristic (0x2BD5).

   org.bluetooth.characteristic.particulate_matter_pm1_concentration

   PM1 particulate matter concentration characteristic (0x2BD7).

   Represents particulate matter PM1 concentration in micrograms per
   cubic meter with a resolution of 1 μg/m³.


   .. py:attribute:: max_value
      :type:  float
      :value: 65533.0



   .. py:attribute:: resolution
      :type:  float
      :value: 1.0



