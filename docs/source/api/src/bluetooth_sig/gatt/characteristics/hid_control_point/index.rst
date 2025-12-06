src.bluetooth_sig.gatt.characteristics.hid_control_point
========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.hid_control_point

.. autoapi-nested-parse::

   HID Control Point characteristic implementation.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.hid_control_point.HID_CONTROL_POINT_DATA_LENGTH


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.hid_control_point.HidControlPointCharacteristic
   src.bluetooth_sig.gatt.characteristics.hid_control_point.HidControlPointCommand


Module Contents
---------------

.. py:class:: HidControlPointCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   HID Control Point characteristic (0x2A4C).

   org.bluetooth.characteristic.hid_control_point

   HID Control Point characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> HidControlPointCommand

      Parse HID control point data.

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional context.

      :returns: Control point command.



   .. py:method:: encode_value(data: HidControlPointCommand) -> bytearray

      Encode control point command back to bytes.

      :param data: Control point command to encode

      :returns: Encoded bytes



.. py:class:: HidControlPointCommand

   Bases: :py:obj:`enum.IntEnum`


   HID Control Point commands.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: EXIT_SUSPEND
      :value: 1



   .. py:attribute:: SUSPEND
      :value: 0



.. py:data:: HID_CONTROL_POINT_DATA_LENGTH
   :value: 1


