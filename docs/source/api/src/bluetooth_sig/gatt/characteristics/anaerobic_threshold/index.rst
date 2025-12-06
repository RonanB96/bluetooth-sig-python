src.bluetooth_sig.gatt.characteristics.anaerobic_threshold
==========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.anaerobic_threshold

.. autoapi-nested-parse::

   Anaerobic Threshold characteristic (0x2A83).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.anaerobic_threshold.AnaerobicThresholdCharacteristic


Module Contents
---------------

.. py:class:: AnaerobicThresholdCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Anaerobic Threshold characteristic (0x2A83).

   org.bluetooth.characteristic.anaerobic_threshold

   Anaerobic Threshold characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


