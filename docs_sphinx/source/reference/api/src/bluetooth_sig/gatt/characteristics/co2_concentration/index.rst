src.bluetooth_sig.gatt.characteristics.co2_concentration
========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.co2_concentration

.. autoapi-nested-parse::

   CO2 Concentration characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.co2_concentration.CO2ConcentrationCharacteristic


Module Contents
---------------

.. py:class:: CO2ConcentrationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Carbon Dioxide concentration characteristic (0x2B8C).

   YAML registry name uses LaTeX subscript form ("CO\\textsubscript{2} Concentration").
   We restore explicit `_characteristic_name` so UUID resolution succeeds because
   the automatic CamelCase splitter cannot derive the LaTeX form from the class name.

   Represents carbon dioxide concentration in parts per million (ppm)
   with a resolution of 1 ppm.


   .. py:attribute:: resolution
      :type:  float
      :value: 1.0



   .. py:attribute:: max_value
      :type:  int | float | None
      :value: 65533.0



