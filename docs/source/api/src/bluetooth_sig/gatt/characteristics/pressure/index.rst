src.bluetooth_sig.gatt.characteristics.pressure
===============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.pressure

.. autoapi-nested-parse::

   Pressure characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.pressure.PressureCharacteristic


Module Contents
---------------

.. py:class:: PressureCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Pressure characteristic (0x2A6D).

   org.bluetooth.characteristic.pressure

   Atmospheric pressure characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:attribute:: max_value
      :type:  float
      :value: 200000.0



