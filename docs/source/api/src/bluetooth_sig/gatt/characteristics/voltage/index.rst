src.bluetooth_sig.gatt.characteristics.voltage
==============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.voltage

.. autoapi-nested-parse::

   Voltage characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.voltage.VoltageCharacteristic


Module Contents
---------------

.. py:class:: VoltageCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Voltage characteristic (0x2B18).

   org.bluetooth.characteristic.voltage

   Voltage characteristic.

   Measures voltage with 1/64 V resolution.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:attribute:: max_value
      :type:  float
      :value: 1023.984375



   .. py:attribute:: resolution
      :type:  float
      :value: 0.015625



