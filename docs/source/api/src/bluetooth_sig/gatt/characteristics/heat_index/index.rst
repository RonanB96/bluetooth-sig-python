src.bluetooth_sig.gatt.characteristics.heat_index
=================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.heat_index

.. autoapi-nested-parse::

   Heat Index characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.heat_index.HeatIndexCharacteristic


Module Contents
---------------

.. py:class:: HeatIndexCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Heat Index characteristic (0x2A7A).

   org.bluetooth.characteristic.heat_index

   Heat Index measurement characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


