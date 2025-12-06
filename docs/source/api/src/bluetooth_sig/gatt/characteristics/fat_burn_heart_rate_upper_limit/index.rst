src.bluetooth_sig.gatt.characteristics.fat_burn_heart_rate_upper_limit
======================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.fat_burn_heart_rate_upper_limit

.. autoapi-nested-parse::

   Fat Burn Heart Rate Upper Limit characteristic (0x2A89).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.fat_burn_heart_rate_upper_limit.FatBurnHeartRateUpperLimitCharacteristic


Module Contents
---------------

.. py:class:: FatBurnHeartRateUpperLimitCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Fat Burn Heart Rate Upper Limit characteristic (0x2A89).

   org.bluetooth.characteristic.fat_burn_heart_rate_upper_limit

   Fat Burn Heart Rate Upper Limit characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


