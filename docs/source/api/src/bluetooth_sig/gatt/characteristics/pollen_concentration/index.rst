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

.. py:class:: PollenConcentrationCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Pollen concentration measurement characteristic (0x2A75).

   Uses uint24 (3 bytes) format as per SIG specification.
   Unit: grains/m³ (count per cubic meter)

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:attribute:: resolution
      :type:  float
      :value: 1.0



