src.bluetooth_sig.gatt.characteristics.true_wind_speed
======================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.true_wind_speed

.. autoapi-nested-parse::

   True Wind Speed characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.true_wind_speed.TrueWindSpeedCharacteristic


Module Contents
---------------

.. py:class:: TrueWindSpeedCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   True Wind Speed characteristic (0x2A70).

   org.bluetooth.characteristic.true_wind_speed

   True Wind Speed measurement characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


