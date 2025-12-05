src.bluetooth_sig.gatt.characteristics.report_map
=================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.report_map

.. autoapi-nested-parse::

   Report Map characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.report_map.ReportMapData
   src.bluetooth_sig.gatt.characteristics.report_map.ReportMapCharacteristic


Module Contents
---------------

.. py:class:: ReportMapData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Report Map characteristic.

   .. attribute:: data

      Report map data bytes (up to 512 octets)


   .. py:attribute:: data
      :type:  bytes


.. py:class:: ReportMapCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Report Map characteristic (0x2A4B).

   org.bluetooth.characteristic.report_map

   Report Map characteristic.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> ReportMapData

      Parse report map data.

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional context.

      :returns: ReportMapData containing the report map bytes.



   .. py:method:: encode_value(data: ReportMapData) -> bytearray

      Encode report map back to bytes.

      :param data: ReportMapData instance to encode

      :returns: Encoded bytes



