src.bluetooth_sig.gatt.characteristics.pulse_oximetry_measurement
=================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.pulse_oximetry_measurement

.. autoapi-nested-parse::

   Pulse Oximetry Measurement characteristic implementation.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.pulse_oximetry_measurement.logger


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.pulse_oximetry_measurement.PulseOximetryData
   src.bluetooth_sig.gatt.characteristics.pulse_oximetry_measurement.PulseOximetryFlags
   src.bluetooth_sig.gatt.characteristics.pulse_oximetry_measurement.PulseOximetryMeasurementCharacteristic


Module Contents
---------------

.. py:class:: PulseOximetryData

   Bases: :py:obj:`msgspec.Struct`


   Parsed pulse oximetry measurement data.

   .. attribute:: spo2

      Blood oxygen saturation percentage (SpO2)

   .. attribute:: pulse_rate

      Pulse rate in beats per minute

   .. attribute:: timestamp

      Optional timestamp of the measurement

   .. attribute:: measurement_status

      Optional measurement status flags

   .. attribute:: device_status

      Optional device status flags

   .. attribute:: pulse_amplitude_index

      Optional pulse amplitude index value

   .. attribute:: supported_features

      Optional PLX features from context (PLXFeatureFlags enum)


   .. py:attribute:: device_status
      :type:  int | None
      :value: None



   .. py:attribute:: measurement_status
      :type:  int | None
      :value: None



   .. py:attribute:: pulse_amplitude_index
      :type:  float | None
      :value: None



   .. py:attribute:: pulse_rate
      :type:  float


   .. py:attribute:: spo2
      :type:  float


   .. py:attribute:: supported_features
      :type:  src.bluetooth_sig.gatt.characteristics.plx_features.PLXFeatureFlags | None
      :value: None



   .. py:attribute:: timestamp
      :type:  datetime.datetime | None
      :value: None



.. py:class:: PulseOximetryFlags

   Bases: :py:obj:`enum.IntFlag`


   Pulse Oximetry measurement flags.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: DEVICE_STATUS_PRESENT
      :value: 4



   .. py:attribute:: MEASUREMENT_STATUS_PRESENT
      :value: 2



   .. py:attribute:: PULSE_AMPLITUDE_INDEX_PRESENT
      :value: 8



   .. py:attribute:: TIMESTAMP_PRESENT
      :value: 1



.. py:class:: PulseOximetryMeasurementCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   PLX Continuous Measurement characteristic (0x2A5F).

   Used to transmit SpO2 (blood oxygen saturation) and pulse rate
   measurements.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> PulseOximetryData

      Parse pulse oximetry measurement data according to Bluetooth specification.

      Format: Flags(1) + SpO2(2) + Pulse Rate(2) + [Timestamp(7)] +
      [Measurement Status(2)] + [Device Status(3)] + [Pulse Amplitude Index(2)]
      SpO2 and Pulse Rate are IEEE-11073 16-bit SFLOAT.

      Context Enhancement:
          If ctx is provided, this method will attempt to enhance the parsed data with:
          - PLX Features (0x2A60): Device capabilities and supported measurement types

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: PulseOximetryData containing parsed pulse oximetry data with optional
                context-enhanced information.



   .. py:method:: encode_value(data: PulseOximetryData) -> bytearray

      Encode pulse oximetry measurement value back to bytes.

      :param data: PulseOximetryData instance to encode

      :returns: Encoded bytes representing the measurement



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: True



   .. py:attribute:: max_length
      :type:  int | None
      :value: 16



   .. py:attribute:: min_length
      :type:  int | None
      :value: 5



.. py:data:: logger

