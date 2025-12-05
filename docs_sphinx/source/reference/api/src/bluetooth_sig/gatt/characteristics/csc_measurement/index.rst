src.bluetooth_sig.gatt.characteristics.csc_measurement
======================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.csc_measurement

.. autoapi-nested-parse::

   CSC Measurement characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.csc_measurement.CSCMeasurementFlags
   src.bluetooth_sig.gatt.characteristics.csc_measurement.CSCMeasurementData
   src.bluetooth_sig.gatt.characteristics.csc_measurement.CSCMeasurementCharacteristic


Module Contents
---------------

.. py:class:: CSCMeasurementFlags

   Bases: :py:obj:`enum.IntFlag`


   CSC Measurement flags as per Bluetooth SIG specification.


   .. py:attribute:: WHEEL_REVOLUTION_DATA_PRESENT
      :value: 1



   .. py:attribute:: CRANK_REVOLUTION_DATA_PRESENT
      :value: 2



.. py:class:: CSCMeasurementData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from CSC Measurement characteristic.


   .. py:attribute:: flags
      :type:  CSCMeasurementFlags


   .. py:attribute:: cumulative_wheel_revolutions
      :type:  int | None
      :value: None



   .. py:attribute:: last_wheel_event_time
      :type:  float | None
      :value: None



   .. py:attribute:: cumulative_crank_revolutions
      :type:  int | None
      :value: None



   .. py:attribute:: last_crank_event_time
      :type:  float | None
      :value: None



.. py:class:: CSCMeasurementCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   CSC (Cycling Speed and Cadence) Measurement characteristic (0x2A5B).

   Used to transmit cycling speed and cadence data.


   .. py:attribute:: CSC_TIME_RESOLUTION
      :value: 1024.0



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> CSCMeasurementData

      Parse CSC measurement data according to Bluetooth specification.

      Format: Flags(1) + [Cumulative Wheel Revolutions(4)] + [Last Wheel Event Time(2)] +
      [Cumulative Crank Revolutions(2)] + [Last Crank Event Time(2)]

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: CSCMeasurementData containing parsed CSC data.

      :raises ValueError: If data format is invalid.



   .. py:method:: encode_value(data: CSCMeasurementData) -> bytearray

      Encode CSC measurement value back to bytes.

      :param data: CSCMeasurementData containing CSC measurement data

      :returns: Encoded bytes representing the CSC measurement



