src.bluetooth_sig.gatt.characteristics.email_address
====================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.email_address

.. autoapi-nested-parse::

   Email Address characteristic (0x2A88).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.email_address.EmailAddressCharacteristic


Module Contents
---------------

.. py:class:: EmailAddressCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Email Address characteristic (0x2A88).

   org.bluetooth.characteristic.email_address

   Email Address characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


