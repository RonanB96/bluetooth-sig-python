src.bluetooth_sig.gatt.characteristics.middle_name
==================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.middle_name

.. autoapi-nested-parse::

   Middle Name characteristic (0x2B48).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.middle_name.MiddleNameCharacteristic


Module Contents
---------------

.. py:class:: MiddleNameCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Middle Name characteristic (0x2B48).

   org.bluetooth.characteristic.middle_name

   Middle Name characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


