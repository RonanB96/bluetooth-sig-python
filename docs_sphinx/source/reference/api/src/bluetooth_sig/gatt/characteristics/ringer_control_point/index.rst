src.bluetooth_sig.gatt.characteristics.ringer_control_point
===========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.ringer_control_point

.. autoapi-nested-parse::

   Ringer Control Point characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.ringer_control_point.RingerControlCommand
   src.bluetooth_sig.gatt.characteristics.ringer_control_point.RingerControlPointData
   src.bluetooth_sig.gatt.characteristics.ringer_control_point.RingerControlPointCharacteristic


Module Contents
---------------

.. py:class:: RingerControlCommand

   Bases: :py:obj:`enum.IntEnum`


   Ringer Control Point command values.


   .. py:attribute:: SILENT_MODE
      :value: 1



   .. py:attribute:: MUTE_ONCE
      :value: 2



   .. py:attribute:: CANCEL_SILENT_MODE
      :value: 3



.. py:class:: RingerControlPointData

   Bases: :py:obj:`msgspec.Struct`


   Data for Ringer Control Point characteristic commands.


   .. py:attribute:: command
      :type:  RingerControlCommand


.. py:class:: RingerControlPointCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Ringer Control Point characteristic (0x2A40).

   org.bluetooth.characteristic.ringer_control_point

   The Ringer Control Point characteristic defines the Control Point of Ringer.
   This is a write-only characteristic used to control ringer behaviour.

   Commands:
   - 1: Silent Mode (sets ringer to silent)
   - 2: Mute Once (silences ringer once)
   - 3: Cancel Silent Mode (sets ringer to normal)
   - 0, 4-255: Reserved for future use


   .. py:method:: encode_value(data: RingerControlPointData) -> bytearray

      Encode RingerControlPointData command to bytes.

      :param data: RingerControlPointData instance to encode

      :returns: Encoded bytes representing the ringer control command



