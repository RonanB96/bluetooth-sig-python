src.bluetooth_sig.gatt.characteristics.electric_current
=======================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.electric_current

.. autoapi-nested-parse::

   Electric Current characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.electric_current.ElectricCurrentCharacteristic


Module Contents
---------------

.. py:class:: ElectricCurrentCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Electric Current characteristic (0x2AEE).

   org.bluetooth.characteristic.electric_current

   Electric Current characteristic.

   Measures electric current with 0.01 A resolution.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:attribute:: max_value
      :type:  float
      :value: 655.35



   .. py:attribute:: resolution
      :type:  float
      :value: 0.01



