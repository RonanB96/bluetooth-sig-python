src.bluetooth_sig.gatt.characteristics.glucose_measurement
==========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.glucose_measurement

.. autoapi-nested-parse::

   Glucose Measurement characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.glucose_measurement.GlucoseMeasurementBits
   src.bluetooth_sig.gatt.characteristics.glucose_measurement.GlucoseType
   src.bluetooth_sig.gatt.characteristics.glucose_measurement.SampleLocation
   src.bluetooth_sig.gatt.characteristics.glucose_measurement.GlucoseMeasurementFlags
   src.bluetooth_sig.gatt.characteristics.glucose_measurement.GlucoseMeasurementData
   src.bluetooth_sig.gatt.characteristics.glucose_measurement.GlucoseMeasurementCharacteristic


Module Contents
---------------

.. py:class:: GlucoseMeasurementBits

   Glucose measurement bit field constants.


   .. py:attribute:: GLUCOSE_TYPE_SAMPLE_MASK
      :value: 15



   .. py:attribute:: GLUCOSE_TYPE_START_BIT
      :value: 4



   .. py:attribute:: GLUCOSE_TYPE_BIT_WIDTH
      :value: 4



   .. py:attribute:: GLUCOSE_SAMPLE_LOCATION_START_BIT
      :value: 0



   .. py:attribute:: GLUCOSE_SAMPLE_LOCATION_BIT_WIDTH
      :value: 4



.. py:class:: GlucoseType

   Bases: :py:obj:`enum.IntEnum`


   Glucose sample type enumeration as per Bluetooth SIG specification.


   .. py:attribute:: CAPILLARY_WHOLE_BLOOD
      :value: 1



   .. py:attribute:: CAPILLARY_PLASMA
      :value: 2



   .. py:attribute:: VENOUS_WHOLE_BLOOD
      :value: 3



   .. py:attribute:: VENOUS_PLASMA
      :value: 4



   .. py:attribute:: ARTERIAL_WHOLE_BLOOD
      :value: 5



   .. py:attribute:: ARTERIAL_PLASMA
      :value: 6



   .. py:attribute:: UNDETERMINED_WHOLE_BLOOD
      :value: 7



   .. py:attribute:: UNDETERMINED_PLASMA
      :value: 8



   .. py:attribute:: INTERSTITIAL_FLUID
      :value: 9



   .. py:attribute:: CONTROL_SOLUTION
      :value: 10



.. py:class:: SampleLocation

   Bases: :py:obj:`enum.IntEnum`


   Sample location enumeration as per Bluetooth SIG specification.


   .. py:attribute:: FINGER
      :value: 1



   .. py:attribute:: ALTERNATE_SITE_TEST
      :value: 2



   .. py:attribute:: EARLOBE
      :value: 3



   .. py:attribute:: CONTROL_SOLUTION
      :value: 4



   .. py:attribute:: NOT_AVAILABLE
      :value: 15



.. py:class:: GlucoseMeasurementFlags

   Bases: :py:obj:`enum.IntFlag`


   Glucose Measurement flags as per Bluetooth SIG specification.


   .. py:attribute:: TIME_OFFSET_PRESENT
      :value: 1



   .. py:attribute:: GLUCOSE_CONCENTRATION_UNITS_MMOL_L
      :value: 2



   .. py:attribute:: TYPE_SAMPLE_LOCATION_PRESENT
      :value: 4



   .. py:attribute:: SENSOR_STATUS_ANNUNCIATION_PRESENT
      :value: 8



.. py:class:: GlucoseMeasurementData

   Bases: :py:obj:`msgspec.Struct`


   Parsed glucose measurement data.


   .. py:attribute:: sequence_number
      :type:  int


   .. py:attribute:: base_time
      :type:  datetime.datetime


   .. py:attribute:: glucose_concentration
      :type:  float


   .. py:attribute:: unit
      :type:  str


   .. py:attribute:: flags
      :type:  GlucoseMeasurementFlags


   .. py:attribute:: time_offset_minutes
      :type:  int | None
      :value: None



   .. py:attribute:: glucose_type
      :type:  GlucoseType | None
      :value: None



   .. py:attribute:: sample_location
      :type:  SampleLocation | None
      :value: None



   .. py:attribute:: sensor_status
      :type:  int | None
      :value: None



   .. py:attribute:: min_length
      :type:  int
      :value: 12



   .. py:attribute:: max_length
      :type:  int
      :value: 17



   .. py:method:: is_reserved_range(value: int) -> bool
      :staticmethod:


      Check if glucose type or sample location is in reserved range.



.. py:class:: GlucoseMeasurementCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Glucose Measurement characteristic (0x2A18).

   Used to transmit glucose concentration measurements with timestamps
   and status. Core characteristic for glucose monitoring devices.


   .. py:attribute:: min_length
      :type:  int
      :value: 12



   .. py:attribute:: max_length
      :type:  int
      :value: 17



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: True



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> GlucoseMeasurementData

      Parse glucose measurement data according to Bluetooth specification.

      Format: Flags(1) + Sequence Number(2) + Base Time(7) + [Time Offset(2)] +
              Glucose Concentration(2) + [Type-Sample Location(1)] + [Sensor Status(2)].

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: GlucoseMeasurementData containing parsed glucose measurement data with metadata.

      :raises ValueError: If data format is invalid.



   .. py:method:: encode_value(data: GlucoseMeasurementData) -> bytearray

      Encode glucose measurement value back to bytes.

      :param data: GlucoseMeasurementData containing glucose measurement data

      :returns: Encoded bytes representing the glucose measurement



