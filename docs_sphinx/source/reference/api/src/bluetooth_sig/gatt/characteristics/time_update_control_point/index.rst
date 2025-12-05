src.bluetooth_sig.gatt.characteristics.time_update_control_point
================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.time_update_control_point

.. autoapi-nested-parse::

   Time Update Control Point characteristic (0x2A16) implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.time_update_control_point.TimeUpdateControlPointCommand
   src.bluetooth_sig.gatt.characteristics.time_update_control_point.TimeUpdateControlPointCharacteristic


Module Contents
---------------

.. py:class:: TimeUpdateControlPointCommand

   Bases: :py:obj:`enum.IntEnum`


   Time Update Control Point commands.


   .. py:attribute:: GET_REFERENCE_UPDATE
      :value: 1



   .. py:attribute:: CANCEL_REFERENCE_UPDATE
      :value: 2



.. py:class:: TimeUpdateControlPointCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Time Update Control Point characteristic.

   Allows a client to request or cancel reference time updates.

   Value: uint8 command
   - 0x01: Get Reference Time Update
   - 0x02: Cancel Reference Time Update


   .. py:method:: decode_value(data: bytearray, ctx: bluetooth_sig.types.context.CharacteristicContext | None = None) -> TimeUpdateControlPointCommand

      Decode the raw data to TimeUpdateControlPointCommand.



   .. py:method:: encode_value(data: TimeUpdateControlPointCommand) -> bytearray

      Encode TimeUpdateControlPointCommand to bytes.



