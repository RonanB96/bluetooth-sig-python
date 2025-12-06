src.bluetooth_sig.gatt.characteristics.indoor_positioning_configuration
=======================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.indoor_positioning_configuration

.. autoapi-nested-parse::

   Indoor Positioning Configuration characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.indoor_positioning_configuration.IndoorPositioningConfigurationCharacteristic


Module Contents
---------------

.. py:class:: IndoorPositioningConfigurationCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Indoor Positioning Configuration characteristic (0x2AAD).

   org.bluetooth.characteristic.indoor_positioning_configuration

   Indoor Positioning Configuration characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


