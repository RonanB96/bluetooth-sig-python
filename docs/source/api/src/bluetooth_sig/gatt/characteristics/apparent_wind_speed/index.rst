src.bluetooth_sig.gatt.characteristics.apparent_wind_speed
==========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.apparent_wind_speed

.. autoapi-nested-parse::

   Apparent Wind Speed characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.apparent_wind_speed.ApparentWindSpeedCharacteristic


Module Contents
---------------

.. py:class:: ApparentWindSpeedCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Apparent Wind Speed characteristic (0x2A72).

   org.bluetooth.characteristic.apparent_wind_speed

   Apparent Wind Speed measurement characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


