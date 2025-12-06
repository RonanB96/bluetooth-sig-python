src.bluetooth_sig.gatt.characteristics.rsc_measurement
======================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.rsc_measurement

.. autoapi-nested-parse::

   RSC Measurement characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.rsc_measurement.RSCMeasurementCharacteristic
   src.bluetooth_sig.gatt.characteristics.rsc_measurement.RSCMeasurementData
   src.bluetooth_sig.gatt.characteristics.rsc_measurement.RSCMeasurementFlags


Module Contents
---------------

.. py:class:: RSCMeasurementCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   RSC (Running Speed and Cadence) Measurement characteristic (0x2A53).

   Used to transmit running speed and cadence data.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> RSCMeasurementData

      Parse RSC measurement data according to Bluetooth specification.

      Format: Flags(1) + Instantaneous Speed(2) + Instantaneous Cadence(1) +
      [Instantaneous Stride Length(2)] + [Total Distance(4)].

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: RSCMeasurementData containing parsed RSC data.

      :raises ValueError: If data format is invalid.



   .. py:method:: encode_value(data: RSCMeasurementData) -> bytearray

      Encode RSC measurement value back to bytes.

      :param data: RSCMeasurementData containing RSC measurement data

      :returns: Encoded bytes representing the RSC measurement



.. py:class:: RSCMeasurementData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from RSC Measurement characteristic.


   .. py:attribute:: flags
      :type:  RSCMeasurementFlags


   .. py:attribute:: instantaneous_cadence
      :type:  int


   .. py:attribute:: instantaneous_speed
      :type:  float


   .. py:attribute:: instantaneous_stride_length
      :type:  float | None
      :value: None



   .. py:attribute:: total_distance
      :type:  float | None
      :value: None



.. py:class:: RSCMeasurementFlags

   Bases: :py:obj:`enum.IntFlag`


   RSC Measurement flags as per Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: INSTANTANEOUS_STRIDE_LENGTH_PRESENT
      :value: 1



   .. py:attribute:: TOTAL_DISTANCE_PRESENT
      :value: 2



