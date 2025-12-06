src.bluetooth_sig.gatt.characteristics.last_name
================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.last_name

.. autoapi-nested-parse::

   Last Name characteristic (0x2A91).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.last_name.LastNameCharacteristic


Module Contents
---------------

.. py:class:: LastNameCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Last Name characteristic (0x2A91).

   org.bluetooth.characteristic.last_name

   Last Name characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


