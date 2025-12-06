src.bluetooth_sig.gatt.characteristics.average_current
======================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.average_current

.. autoapi-nested-parse::

   Average Current characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.average_current.AverageCurrentCharacteristic


Module Contents
---------------

.. py:class:: AverageCurrentCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Average Current characteristic (0x2AE0).

   org.bluetooth.characteristic.average_current

   Average Current characteristic.

   Measures average electric current with 0.01 A resolution.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:attribute:: resolution
      :type:  float
      :value: 0.01



