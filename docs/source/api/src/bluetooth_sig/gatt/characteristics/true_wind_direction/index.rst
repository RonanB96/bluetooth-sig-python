src.bluetooth_sig.gatt.characteristics.true_wind_direction
==========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.true_wind_direction

.. autoapi-nested-parse::

   True Wind Direction characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.true_wind_direction.TrueWindDirectionCharacteristic


Module Contents
---------------

.. py:class:: TrueWindDirectionCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   True Wind Direction characteristic (0x2A71).

   org.bluetooth.characteristic.true_wind_direction

   True Wind Direction measurement characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


