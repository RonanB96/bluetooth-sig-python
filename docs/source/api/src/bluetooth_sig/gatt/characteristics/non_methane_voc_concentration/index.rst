src.bluetooth_sig.gatt.characteristics.non_methane_voc_concentration
====================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.non_methane_voc_concentration

.. autoapi-nested-parse::

   Non-Methane Volatile Organic Compounds Concentration characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.non_methane_voc_concentration.NonMethaneVOCConcentrationCharacteristic


Module Contents
---------------

.. py:class:: NonMethaneVOCConcentrationCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Non-Methane Volatile Organic Compounds concentration characteristic (0x2BD3).

   Uses IEEE 11073 SFLOAT format (medfloat16) as per SIG specification.
   Unit: kg/m³ (kilogram per cubic meter)

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


