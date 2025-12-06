src.bluetooth_sig.gatt.characteristics.stride_length
====================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.stride_length

.. autoapi-nested-parse::

   Stride Length characteristic (0x2B49).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.stride_length.StrideLengthCharacteristic


Module Contents
---------------

.. py:class:: StrideLengthCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Stride Length characteristic (0x2B49).

   org.bluetooth.characteristic.stride_length

   Stride Length characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


