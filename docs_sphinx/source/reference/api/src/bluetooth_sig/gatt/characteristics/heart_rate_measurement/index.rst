src.bluetooth_sig.gatt.characteristics.heart_rate_measurement
=============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.heart_rate_measurement

.. autoapi-nested-parse::

   Heart Rate Measurement characteristic implementation.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.heart_rate_measurement.logger
   src.bluetooth_sig.gatt.characteristics.heart_rate_measurement.RR_INTERVAL_RESOLUTION


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.heart_rate_measurement.HeartRateMeasurementFlags
   src.bluetooth_sig.gatt.characteristics.heart_rate_measurement.SensorContactState
   src.bluetooth_sig.gatt.characteristics.heart_rate_measurement.HeartRateData
   src.bluetooth_sig.gatt.characteristics.heart_rate_measurement.HeartRateMeasurementCharacteristic


Module Contents
---------------

.. py:data:: logger

.. py:data:: RR_INTERVAL_RESOLUTION
   :value: 1024.0


.. py:class:: HeartRateMeasurementFlags

   Bases: :py:obj:`enum.IntFlag`


   Heart Rate Measurement flags as per Bluetooth SIG specification.


   .. py:attribute:: HEART_RATE_VALUE_FORMAT_UINT16
      :value: 1



   .. py:attribute:: SENSOR_CONTACT_SUPPORTED
      :value: 2



   .. py:attribute:: SENSOR_CONTACT_DETECTED
      :value: 4



   .. py:attribute:: ENERGY_EXPENDED_PRESENT
      :value: 8



   .. py:attribute:: RR_INTERVAL_PRESENT
      :value: 16



.. py:class:: SensorContactState

   Bases: :py:obj:`enum.IntEnum`


   Sensor contact state enumeration.


   .. py:attribute:: NOT_SUPPORTED
      :value: 0



   .. py:attribute:: NOT_DETECTED
      :value: 1



   .. py:attribute:: DETECTED
      :value: 2



   .. py:method:: from_flags(flags: int) -> SensorContactState
      :classmethod:


      Create enum from heart rate flags.



.. py:class:: HeartRateData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Heart Rate Measurement characteristic.

   .. attribute:: heart_rate

      Heart rate in beats per minute (0-UINT16_MAX)

   .. attribute:: sensor_contact

      State of sensor contact detection

   .. attribute:: energy_expended

      Optional energy expended in kilojoules

   .. attribute:: rr_intervals

      Tuple of R-R intervals in seconds (immutable)

   .. attribute:: flags

      Raw flags byte for reference

   .. attribute:: sensor_location

      Optional body sensor location from context (BodySensorLocation enum)


   .. py:attribute:: heart_rate
      :type:  int


   .. py:attribute:: sensor_contact
      :type:  SensorContactState


   .. py:attribute:: energy_expended
      :type:  int | None
      :value: None



   .. py:attribute:: rr_intervals
      :type:  tuple[float, Ellipsis]
      :value: ()



   .. py:attribute:: flags
      :type:  HeartRateMeasurementFlags


   .. py:attribute:: sensor_location
      :type:  src.bluetooth_sig.gatt.characteristics.body_sensor_location.BodySensorLocation | None
      :value: None



.. py:class:: HeartRateMeasurementCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Heart Rate Measurement characteristic (0x2A37).

   Used in Heart Rate Service (spec: Heart Rate Service 1.0, Heart Rate Profile 1.0)
   to transmit instantaneous heart rate plus optional energy expended and
   RR-Interval metrics.

   Specification summary (flags byte bit assignments - see adopted spec & Errata 23224):
     Bit 0 (0x01): Heart Rate Value Format (0 = uint8, 1 = uint16)
     Bit 1 (0x02): Sensor Contact Supported
     Bit 2 (0x04): Sensor Contact Detected (valid only when Bit1 set)
     Bit 3 (0x08): Energy Expended Present (adds 2 bytes, little-endian, in kilo Joules)
     Bit 4 (0x10): RR-Interval(s) Present (sequence of 16-bit values, units 1/1024 s)
     Bits 5-7: Reserved (must be 0)

   Parsing Rules:
     * Minimum length: 2 bytes (flags + at least one byte of heart rate value)
     * If Bit0 set, heart rate is 16 bits; else 8 bits
     * Energy Expended only parsed if flag set AND 2 bytes remain
     * RR-Intervals parsed greedily in pairs until buffer end when flag set
     * RR-Interval raw value converted to seconds: raw / 1024.0
     * Sensor contact state derived from Bits1/2 tri-state (not supported, not detected, detected)

   Validation:
     * Heart rate validated within 0..UINT16_MAX (spec does not strictly define upper physiological bound)
     * RR interval constrained to 0.0-65.535 s (fits 16-bit / 1024 scaling and guards against malformed data)
     * Energy expended 0..UINT16_MAX

   .. rubric:: References

   * Bluetooth SIG Heart Rate Service 1.0 (https://www.bluetooth.com/specifications/specs/heart-rate-service-1-0/)
   * Bluetooth SIG Heart Rate Profile 1.0 (https://www.bluetooth.com/specifications/specs/heart-rate-profile-1-0/)
   * Errata Correction 23224 (mandatory for compliance)


   .. py:attribute:: RR_INTERVAL_RESOLUTION
      :value: 1024.0



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> HeartRateData

      Parse heart rate measurement data according to Bluetooth specification.

      Format: Flags(1) + Heart Rate Value(1-2) + [Energy Expended(2)] + [RR-Intervals(2*n)]

      Context Enhancement:
          If ctx is provided, this method will attempt to enhance the parsed data with:
          - Body Sensor Location (0x2A38): Location where the sensor is positioned

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: HeartRateData containing parsed heart rate data with metadata and optional
                context-enhanced information.



   .. py:method:: encode_value(data: HeartRateData) -> bytearray

      Encode HeartRateData back to bytes.

      The inverse of decode_value respecting the same flag semantics.

      :param data: HeartRateData instance to encode

      :returns: Encoded bytes representing the heart rate measurement



