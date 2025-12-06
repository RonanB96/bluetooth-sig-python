src.bluetooth_sig.gatt.characteristics.maximum_recommended_heart_rate
=====================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.maximum_recommended_heart_rate

.. autoapi-nested-parse::

   Maximum Recommended Heart Rate characteristic (0x2A91).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.maximum_recommended_heart_rate.MaximumRecommendedHeartRateCharacteristic


Module Contents
---------------

.. py:class:: MaximumRecommendedHeartRateCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Maximum Recommended Heart Rate characteristic (0x2A91).

   org.bluetooth.characteristic.maximum_recommended_heart_rate

   Maximum Recommended Heart Rate characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


