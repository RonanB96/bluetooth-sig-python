src.bluetooth_sig.gatt.characteristics.rainfall
===============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.rainfall

.. autoapi-nested-parse::

   Rainfall characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.rainfall.RainfallCharacteristic


Module Contents
---------------

.. py:class:: RainfallCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Rainfall characteristic (0x2A78).

   org.bluetooth.characteristic.rainfall

   Rainfall characteristic.

   Represents the amount of rain that has fallen in millimeters. Uses
   uint16 with 1 mm resolution (1:1 scaling).

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:attribute:: resolution
      :type:  float
      :value: 1.0



