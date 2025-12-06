src.bluetooth_sig.gatt.characteristics.dew_point
================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.dew_point

.. autoapi-nested-parse::

   Dew Point characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.dew_point.DewPointCharacteristic


Module Contents
---------------

.. py:class:: DewPointCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Dew Point characteristic (0x2A7B).

   org.bluetooth.characteristic.dew_point

   Dew Point measurement characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


