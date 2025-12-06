src.bluetooth_sig.gatt.characteristics.report
=============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.report

.. autoapi-nested-parse::

   Report characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.report.ReportCharacteristic
   src.bluetooth_sig.gatt.characteristics.report.ReportData


Module Contents
---------------

.. py:class:: ReportCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Report characteristic (0x2A4D).

   org.bluetooth.characteristic.report

   Report characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> ReportData

      Parse report data.

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional context.

      :returns: ReportData containing the report bytes.



   .. py:method:: encode_value(data: ReportData) -> bytearray

      Encode report data back to bytes.

      :param data: ReportData instance to encode

      :returns: Encoded bytes



.. py:class:: ReportData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Report characteristic.

   .. attribute:: data

      Report data bytes (variable length)


   .. py:attribute:: data
      :type:  bytes


