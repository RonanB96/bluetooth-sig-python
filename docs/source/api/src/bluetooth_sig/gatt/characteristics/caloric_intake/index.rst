src.bluetooth_sig.gatt.characteristics.caloric_intake
=====================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.caloric_intake

.. autoapi-nested-parse::

   Caloric Intake characteristic (0x2B45).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.caloric_intake.CaloricIntakeCharacteristic


Module Contents
---------------

.. py:class:: CaloricIntakeCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Caloric Intake characteristic (0x2B45).

   org.bluetooth.characteristic.caloric_intake

   Caloric Intake characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


