src.bluetooth_sig.gatt.characteristics.device_wearing_position
==============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.device_wearing_position

.. autoapi-nested-parse::

   Device Wearing Position characteristic (0x2B4B).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.device_wearing_position.DeviceWearingPositionCharacteristic


Module Contents
---------------

.. py:class:: DeviceWearingPositionCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Device Wearing Position characteristic (0x2B4B).

   org.bluetooth.characteristic.device_wearing_position

   Device Wearing Position characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


