src.bluetooth_sig.gatt.characteristics.two_zone_heart_rate_limits
=================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.two_zone_heart_rate_limits

.. autoapi-nested-parse::

   Two Zone Heart Rate Limits characteristic (0x2A95).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.two_zone_heart_rate_limits.TwoZoneHeartRateLimitsCharacteristic


Module Contents
---------------

.. py:class:: TwoZoneHeartRateLimitsCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Two Zone Heart Rate Limits characteristic (0x2A95).

   org.bluetooth.characteristic.two_zone_heart_rate_limits

   Two Zone Heart Rate Limits characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


