src.bluetooth_sig.gatt.characteristics.battery_level
====================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.battery_level

.. autoapi-nested-parse::

   Battery level characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.battery_level.BatteryLevelCharacteristic


Module Contents
---------------

.. py:class:: BatteryLevelCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Battery Level characteristic (0x2A19).

   org.bluetooth.characteristic.battery_level

   Battery level characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


