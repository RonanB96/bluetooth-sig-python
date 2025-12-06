src.bluetooth_sig.gatt.characteristics.alert_level
==================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.alert_level

.. autoapi-nested-parse::

   Alert Level characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.alert_level.AlertLevel
   src.bluetooth_sig.gatt.characteristics.alert_level.AlertLevelCharacteristic


Module Contents
---------------

.. py:class:: AlertLevel

   Bases: :py:obj:`enum.IntEnum`


   Alert level values as defined by Bluetooth SIG.

   Values:
       NO_ALERT: No alert (0x00)
       MILD_ALERT: Mild alert (0x01)
       HIGH_ALERT: High alert (0x02)

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: HIGH_ALERT
      :value: 2



   .. py:attribute:: MILD_ALERT
      :value: 1



   .. py:attribute:: NO_ALERT
      :value: 0



.. py:class:: AlertLevelCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Alert Level characteristic (0x2A06).

   org.bluetooth.characteristic.alert_level

   The Alert Level characteristic defines the level of alert and is
   used by services such as Immediate Alert (0x1802), Link Loss (0x1803),
   and Phone Alert Status (0x180E).

   Valid values:
       - 0x00: No Alert
       - 0x01: Mild Alert
       - 0x02: High Alert
       - 0x03-0xFF: Reserved for Future Use

   Spec: Bluetooth SIG GATT Specification Supplement, Alert Level

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: bluetooth_sig.types.context.CharacteristicContext | None = None) -> AlertLevel

      Decode alert level from raw bytes.

      :param data: Raw bytes from BLE characteristic (1 byte)
      :param ctx: Optional context for parsing

      :returns: AlertLevel enum value

      :raises ValueError: If data is less than 1 byte or value is invalid



   .. py:method:: encode_value(data: AlertLevel | int) -> bytearray

      Encode alert level to raw bytes.

      :param data: AlertLevel enum value or integer (0-2)

      :returns: Encoded characteristic data (1 byte)

      :raises ValueError: If data is not 0, 1, or 2



