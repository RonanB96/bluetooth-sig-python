src.bluetooth_sig.gatt.characteristics.vo2_max
==============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.vo2_max

.. autoapi-nested-parse::

   VO2 Max characteristic (0x2A96).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.vo2_max.VO2MaxCharacteristic


Module Contents
---------------

.. py:class:: VO2MaxCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   VO2 Max characteristic (0x2A96).

   org.bluetooth.characteristic.vo2_max

   VO2 Max characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


