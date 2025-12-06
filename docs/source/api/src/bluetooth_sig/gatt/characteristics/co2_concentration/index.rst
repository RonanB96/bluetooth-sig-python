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

.. py:class:: CO2ConcentrationCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Carbon Dioxide concentration characteristic (0x2B8C).

   YAML registry name uses LaTeX subscript form ("CO\\textsubscript{2} Concentration").
   We restore explicit `_characteristic_name` so UUID resolution succeeds because
   the automatic CamelCase splitter cannot derive the LaTeX form from the class name.

   Represents carbon dioxide concentration in parts per million (ppm)
   with a resolution of 1 ppm.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:attribute:: max_value
      :type:  int | float | None
      :value: 65533.0



   .. py:attribute:: resolution
      :type:  float
      :value: 1.0



