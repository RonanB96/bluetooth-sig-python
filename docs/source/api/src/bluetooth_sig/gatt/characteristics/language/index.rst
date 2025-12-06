src.bluetooth_sig.gatt.characteristics.language
===============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.language

.. autoapi-nested-parse::

   Language characteristic (0x2AA2).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.language.LanguageCharacteristic


Module Contents
---------------

.. py:class:: LanguageCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Language characteristic (0x2AA2).

   org.bluetooth.characteristic.language

   Language characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


