src.bluetooth_sig.gatt.characteristics.blood_pressure_measurement
=================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.blood_pressure_measurement

.. autoapi-nested-parse::

   Blood Pressure Measurement characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.blood_pressure_measurement.BloodPressureData
   src.bluetooth_sig.gatt.characteristics.blood_pressure_measurement.BloodPressureMeasurementCharacteristic
   src.bluetooth_sig.gatt.characteristics.blood_pressure_measurement.BloodPressureMeasurementStatus


Module Contents
---------------

.. py:class:: BloodPressureData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Blood Pressure Measurement characteristic.


   .. py:attribute:: diastolic
      :type:  float


   .. py:attribute:: flags
      :type:  src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BloodPressureFlags


   .. py:attribute:: mean_arterial_pressure
      :type:  float


   .. py:attribute:: optional_fields
      :type:  src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BloodPressureOptionalFields


   .. py:attribute:: systolic
      :type:  float


   .. py:attribute:: unit
      :type:  bluetooth_sig.types.units.PressureUnit


.. py:class:: BloodPressureMeasurementCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BaseBloodPressureCharacteristic`


   Blood Pressure Measurement characteristic (0x2A35).

   Used to transmit blood pressure measurements with systolic,
   diastolic and mean arterial pressure.

   SIG Specification Pattern:
   This characteristic can use Blood Pressure Feature (0x2A49) to interpret
   which status flags are supported by the device.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> BloodPressureData

      Parse blood pressure measurement data according to Bluetooth specification.

      Format: Flags(1) + Systolic(2) + Diastolic(2) + MAP(2) + [Timestamp(7)] +
      [Pulse Rate(2)] + [User ID(1)] + [Measurement Status(2)].
      All pressure values are IEEE-11073 16-bit SFLOAT.

      :param data: Raw bytearray from BLE characteristic
      :param ctx: Optional context providing access to Blood Pressure Feature characteristic
                  for validating which measurement status flags are supported

      :returns: BloodPressureData containing parsed blood pressure data with metadata

      SIG Pattern:
      When context is available, can validate that measurement status flags are
      within the device's supported features as indicated by Blood Pressure Feature.




   .. py:method:: encode_value(data: BloodPressureData) -> bytearray

      Encode BloodPressureData back to bytes.

      :param data: BloodPressureData instance to encode

      :returns: Encoded bytes representing the blood pressure measurement



.. py:class:: BloodPressureMeasurementStatus

   Bases: :py:obj:`enum.IntFlag`


   Blood Pressure Measurement Status flags as per Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: BODY_MOVEMENT_DETECTED
      :value: 1



   .. py:attribute:: CUFF_TOO_LOOSE
      :value: 2



   .. py:attribute:: IMPROPER_MEASUREMENT_POSITION
      :value: 16



   .. py:attribute:: IRREGULAR_PULSE_DETECTED
      :value: 4



   .. py:attribute:: PULSE_RATE_OUT_OF_RANGE
      :value: 8



