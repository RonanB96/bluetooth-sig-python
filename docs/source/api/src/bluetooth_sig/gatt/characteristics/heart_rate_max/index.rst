src.bluetooth_sig.gatt.characteristics.heart_rate_max
=====================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.heart_rate_max

.. autoapi-nested-parse::

   Heart Rate Max characteristic (0x2A8D).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.heart_rate_max.HeartRateMaxCharacteristic


Module Contents
---------------

.. py:class:: HeartRateMaxCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Heart Rate Max characteristic (0x2A8D).

   org.bluetooth.characteristic.heart_rate_max

   Heart Rate Max characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


