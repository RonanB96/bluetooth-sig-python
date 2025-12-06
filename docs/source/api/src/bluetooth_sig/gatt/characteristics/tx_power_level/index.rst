src.bluetooth_sig.gatt.characteristics.tx_power_level
=====================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.tx_power_level

.. autoapi-nested-parse::

   Tx Power Level characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.tx_power_level.TxPowerLevelCharacteristic


Module Contents
---------------

.. py:class:: TxPowerLevelCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Tx Power Level characteristic (0x2A07).

   org.bluetooth.characteristic.tx_power_level

   Tx Power Level characteristic.

   Measures transmit power level in dBm.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


