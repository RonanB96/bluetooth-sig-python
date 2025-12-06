src.bluetooth_sig.gatt.characteristics.high_voltage
===================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.high_voltage

.. autoapi-nested-parse::

   High Voltage characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.high_voltage.HighVoltageCharacteristic


Module Contents
---------------

.. py:class:: HighVoltageCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   High Voltage characteristic (0x2BE0).

   org.bluetooth.characteristic.high_voltage

   High Voltage characteristic.

   Measures high voltage systems using uint24 (3 bytes) format.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:attribute:: resolution
      :type:  float
      :value: 1.0



