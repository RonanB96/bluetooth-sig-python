src.bluetooth_sig.gatt.characteristics.age
==========================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.age

.. autoapi-nested-parse::

   Age characteristic (0x2A80).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.age.AgeCharacteristic


Module Contents
---------------

.. py:class:: AgeCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Age characteristic (0x2A80).

   org.bluetooth.characteristic.age

   Age characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


