src.bluetooth_sig.gatt.characteristics.average_voltage
======================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.average_voltage

.. autoapi-nested-parse::

   Average Voltage characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.average_voltage.AverageVoltageCharacteristic


Module Contents
---------------

.. py:class:: AverageVoltageCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Average Voltage characteristic (0x2AE1).

   org.bluetooth.characteristic.average_voltage

   Average Voltage characteristic.

   Measures average voltage with 1/64 V resolution.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:attribute:: resolution
      :type:  float
      :value: 0.015625



