src.bluetooth_sig.gatt.characteristics.temperature_measurement
==============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.temperature_measurement

.. autoapi-nested-parse::

   Temperature Measurement characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.temperature_measurement.TemperatureMeasurementCharacteristic
   src.bluetooth_sig.gatt.characteristics.temperature_measurement.TemperatureMeasurementData
   src.bluetooth_sig.gatt.characteristics.temperature_measurement.TemperatureMeasurementFlags


Module Contents
---------------

.. py:class:: TemperatureMeasurementCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Temperature Measurement characteristic (0x2A1C).

   Used in Health Thermometer Service for medical temperature readings.
   Different from Environmental Temperature (0x2A6E).


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> TemperatureMeasurementData

      Parse temperature measurement data according to Bluetooth specification.

      Format: Flags(1) + Temperature Value(4) + [Timestamp(7)] + [Temperature Type(1)].
      Temperature is medfloat32 (IEEE 11073 medical float format).

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional context providing surrounding characteristic metadata when available.

      :returns: TemperatureMeasurementData containing parsed temperature data with metadata.



   .. py:method:: encode_value(data: TemperatureMeasurementData) -> bytearray

      Encode temperature measurement value back to bytes.

      :param data: TemperatureMeasurementData containing temperature measurement data

      :returns: Encoded bytes representing the temperature measurement



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: True



   .. py:attribute:: max_length
      :type:  int | None
      :value: 13



   .. py:attribute:: min_length
      :type:  int | None
      :value: 5



.. py:class:: TemperatureMeasurementData

   Bases: :py:obj:`msgspec.Struct`


   Parsed temperature measurement data.


   .. py:attribute:: flags
      :type:  TemperatureMeasurementFlags


   .. py:attribute:: temperature
      :type:  float


   .. py:attribute:: temperature_type
      :type:  int | None
      :value: None



   .. py:attribute:: timestamp
      :type:  datetime.datetime | None
      :value: None



   .. py:attribute:: unit
      :type:  bluetooth_sig.types.units.TemperatureUnit


.. py:class:: TemperatureMeasurementFlags

   Bases: :py:obj:`enum.IntFlag`


   Temperature Measurement flags as per Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: CELSIUS_UNIT
      :value: 0



   .. py:attribute:: FAHRENHEIT_UNIT
      :value: 1



   .. py:attribute:: TEMPERATURE_TYPE_PRESENT
      :value: 4



   .. py:attribute:: TIMESTAMP_PRESENT
      :value: 2



