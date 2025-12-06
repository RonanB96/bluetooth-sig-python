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

.. py:class:: SulfurDioxideConcentrationCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Sulfur Dioxide Concentration characteristic (0x2BD8).

   org.bluetooth.characteristic.sulfur_dioxide_concentration

   Sulfur dioxide concentration measurement characteristic (0x2BD3).

   Represents sulfur dioxide (SO2) concentration in parts per billion
   (ppb) with a resolution of 1 ppb.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:attribute:: max_value
      :type:  float
      :value: 65533.0



   .. py:attribute:: resolution
      :type:  float
      :value: 1.0



