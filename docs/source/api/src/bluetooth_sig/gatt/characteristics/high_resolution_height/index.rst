src.bluetooth_sig.gatt.characteristics.high_resolution_height
=============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.high_resolution_height

.. autoapi-nested-parse::

   High Resolution Height characteristic (0x2B47).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.high_resolution_height.HighResolutionHeightCharacteristic


Module Contents
---------------

.. py:class:: HighResolutionHeightCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   High Resolution Height characteristic (0x2B47).

   org.bluetooth.characteristic.high_resolution_height

   High Resolution Height characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


