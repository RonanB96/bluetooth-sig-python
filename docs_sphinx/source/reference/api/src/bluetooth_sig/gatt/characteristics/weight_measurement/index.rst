src.bluetooth_sig.gatt.characteristics.weight_measurement
=========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.weight_measurement

.. autoapi-nested-parse::

   Weight Measurement characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.weight_measurement.WeightMeasurementFlags
   src.bluetooth_sig.gatt.characteristics.weight_measurement.WeightMeasurementData
   src.bluetooth_sig.gatt.characteristics.weight_measurement.WeightMeasurementCharacteristic


Module Contents
---------------

.. py:class:: WeightMeasurementFlags

   Bases: :py:obj:`enum.IntFlag`


   Weight Measurement flags as per Bluetooth SIG specification.


   .. py:attribute:: IMPERIAL_UNITS
      :value: 1



   .. py:attribute:: TIMESTAMP_PRESENT
      :value: 2



   .. py:attribute:: USER_ID_PRESENT
      :value: 4



   .. py:attribute:: BMI_PRESENT
      :value: 8



   .. py:attribute:: HEIGHT_PRESENT
      :value: 16



.. py:class:: WeightMeasurementData

   Bases: :py:obj:`msgspec.Struct`


   Parsed weight measurement data.


   .. py:attribute:: weight
      :type:  float


   .. py:attribute:: weight_unit
      :type:  bluetooth_sig.types.units.WeightUnit


   .. py:attribute:: measurement_units
      :type:  bluetooth_sig.types.units.MeasurementSystem


   .. py:attribute:: flags
      :type:  WeightMeasurementFlags


   .. py:attribute:: timestamp
      :type:  datetime.datetime | None
      :value: None



   .. py:attribute:: user_id
      :type:  int | None
      :value: None



   .. py:attribute:: bmi
      :type:  float | None
      :value: None



   .. py:attribute:: height
      :type:  float | None
      :value: None



   .. py:attribute:: height_unit
      :type:  bluetooth_sig.types.units.HeightUnit | None
      :value: None



.. py:class:: WeightMeasurementCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Weight Measurement characteristic (0x2A9D).

   Used to transmit weight measurement data with optional fields.
   Supports metric/imperial units, timestamps, user ID, BMI, and
   height.


   .. py:attribute:: min_length
      :type:  int
      :value: 3



   .. py:attribute:: max_length
      :type:  int
      :value: 21



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: True



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> WeightMeasurementData

      Parse weight measurement data according to Bluetooth specification.

      Format: Flags(1) + Weight(2) + [Timestamp(7)] + [User ID(1)] +
              [BMI(2)] + [Height(2)]

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: WeightMeasurementData containing parsed weight measurement data.

      :raises ValueError: If data format is invalid.



   .. py:method:: encode_value(data: WeightMeasurementData) -> bytearray

      Encode weight measurement value back to bytes.

      :param data: WeightMeasurementData containing weight measurement data

      :returns: Encoded bytes representing the weight measurement



