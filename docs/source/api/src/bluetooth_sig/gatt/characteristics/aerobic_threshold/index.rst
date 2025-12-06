src.bluetooth_sig.gatt.characteristics.aerobic_threshold
========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.aerobic_threshold

.. autoapi-nested-parse::

   Aerobic Threshold characteristic (0x2A7E).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.aerobic_threshold.AerobicThresholdCharacteristic


Module Contents
---------------

.. py:class:: AerobicThresholdCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Aerobic Threshold characteristic (0x2A7E).

   org.bluetooth.characteristic.aerobic_threshold

   Aerobic Threshold characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


