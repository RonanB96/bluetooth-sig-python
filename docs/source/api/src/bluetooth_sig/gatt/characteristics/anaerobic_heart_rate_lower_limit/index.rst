src.bluetooth_sig.gatt.characteristics.anaerobic_heart_rate_lower_limit
=======================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.anaerobic_heart_rate_lower_limit

.. autoapi-nested-parse::

   Anaerobic Heart Rate Lower Limit characteristic (0x2A81).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.anaerobic_heart_rate_lower_limit.AnaerobicHeartRateLowerLimitCharacteristic


Module Contents
---------------

.. py:class:: AnaerobicHeartRateLowerLimitCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Anaerobic Heart Rate Lower Limit characteristic (0x2A81).

   org.bluetooth.characteristic.anaerobic_heart_rate_lower_limit

   Anaerobic Heart Rate Lower Limit characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


