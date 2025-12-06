src.bluetooth_sig.gatt.characteristics.scan_interval_window
===========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.scan_interval_window

.. autoapi-nested-parse::

   Scan Interval Window characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.scan_interval_window.ScanIntervalWindowCharacteristic


Module Contents
---------------

.. py:class:: ScanIntervalWindowCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Scan Interval Window characteristic (0x2A4F).

   org.bluetooth.characteristic.scan_interval_window

   The Scan Interval Window characteristic is used to set the scan interval
   and scan window parameters for BLE scanning.

   This is a write-only characteristic containing:
   - Scan Interval: uint16 (2 bytes, little-endian, units of 0.625ms, range 0x0004-0x4000)
   - Scan Window: uint16 (2 bytes, little-endian, units of 0.625ms, range 0x0004-0x4000)

   The scan window must be less than or equal to the scan interval.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> src.bluetooth_sig.types.scan_interval_window.ScanIntervalWindowData

      Parse scan interval window data.

      :param data: Raw bytearray from BLE characteristic (4 bytes).
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: ScanIntervalWindowData with parsed scan parameters.



   .. py:method:: encode_value(data: src.bluetooth_sig.types.scan_interval_window.ScanIntervalWindowData) -> bytearray

      Encode scan interval window value back to bytes.

      :param data: ScanIntervalWindowData instance

      :returns: Encoded bytes representing the scan parameters (4 bytes)



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: False



   .. py:attribute:: expected_length
      :value: 4



   .. py:attribute:: max_length
      :value: 4



   .. py:attribute:: min_length
      :value: 4



