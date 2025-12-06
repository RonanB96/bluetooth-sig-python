src.bluetooth_sig.gatt.characteristics.resting_heart_rate
=========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.resting_heart_rate

.. autoapi-nested-parse::

   Resting Heart Rate characteristic (0x2A92).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.resting_heart_rate.RestingHeartRateCharacteristic


Module Contents
---------------

.. py:class:: RestingHeartRateCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Resting Heart Rate characteristic (0x2A92).

   org.bluetooth.characteristic.resting_heart_rate

   Resting Heart Rate characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


