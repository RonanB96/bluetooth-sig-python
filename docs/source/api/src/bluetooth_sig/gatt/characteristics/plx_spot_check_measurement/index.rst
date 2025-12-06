src.bluetooth_sig.gatt.characteristics.plx_spot_check_measurement
=================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.plx_spot_check_measurement

.. autoapi-nested-parse::

   PLX Spot-Check Measurement characteristic implementation.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.plx_spot_check_measurement.logger


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.plx_spot_check_measurement.PLXDeviceAndSensorStatus
   src.bluetooth_sig.gatt.characteristics.plx_spot_check_measurement.PLXMeasurementStatus
   src.bluetooth_sig.gatt.characteristics.plx_spot_check_measurement.PLXSpotCheckData
   src.bluetooth_sig.gatt.characteristics.plx_spot_check_measurement.PLXSpotCheckFlags
   src.bluetooth_sig.gatt.characteristics.plx_spot_check_measurement.PLXSpotCheckMeasurementCharacteristic


Module Contents
---------------

.. py:class:: PLXDeviceAndSensorStatus

   Bases: :py:obj:`enum.IntFlag`


   PLX Device and Sensor Status flags (24-bit).

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: DEVICE_DATA_FOR_DEMONSTRATION
      :value: 32



   .. py:attribute:: DEVICE_DATA_FROM_CALIBRATION_TEST
      :value: 128



   .. py:attribute:: DEVICE_DATA_FROM_MEASUREMENT_STORAGE
      :value: 16



   .. py:attribute:: DEVICE_DATA_FROM_TESTING_SIMULATION
      :value: 64



   .. py:attribute:: DEVICE_EARLY_ESTIMATED_DATA
      :value: 2



   .. py:attribute:: DEVICE_FULLY_QUALIFIED_DATA
      :value: 8



   .. py:attribute:: DEVICE_MEASUREMENT_ONGOING
      :value: 1



   .. py:attribute:: DEVICE_VALIDATED_DATA
      :value: 4



   .. py:attribute:: SENSOR_DEFECTIVE
      :value: 512



   .. py:attribute:: SENSOR_DISCONNECTED
      :value: 1024



   .. py:attribute:: SENSOR_MALFUNCTIONING
      :value: 2048



   .. py:attribute:: SENSOR_NOT_OPERATIONAL
      :value: 8192



   .. py:attribute:: SENSOR_OPERATIONAL
      :value: 256



   .. py:attribute:: SENSOR_UNCALIBRATED
      :value: 4096



.. py:class:: PLXMeasurementStatus

   Bases: :py:obj:`enum.IntFlag`


   PLX Measurement Status flags (16-bit).

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: DATA_FOR_DEMONSTRATION
      :value: 32



   .. py:attribute:: DATA_FROM_CALIBRATION_TEST
      :value: 128



   .. py:attribute:: DATA_FROM_MEASUREMENT_STORAGE
      :value: 16



   .. py:attribute:: DATA_FROM_TESTING_SIMULATION
      :value: 64



   .. py:attribute:: EARLY_ESTIMATED_DATA
      :value: 2



   .. py:attribute:: FULLY_QUALIFIED_DATA
      :value: 8



   .. py:attribute:: MEASUREMENT_ONGOING
      :value: 1



   .. py:attribute:: VALIDATED_DATA
      :value: 4



.. py:class:: PLXSpotCheckData

   Bases: :py:obj:`msgspec.Struct`


   Parsed PLX spot-check measurement data.

   .. attribute:: spo2

      Blood oxygen saturation percentage (SpO2)

   .. attribute:: pulse_rate

      Pulse rate in beats per minute

   .. attribute:: spo2pr_fast

      Optional flag indicating if SpO2PR is fast (True) or normal (False)

   .. attribute:: measurement_status

      Optional measurement status flags

   .. attribute:: device_and_sensor_status

      Optional device and sensor status flags

   .. attribute:: pulse_amplitude_index

      Optional pulse amplitude index value

   .. attribute:: supported_features

      Optional PLX features from context (PLXFeatureFlags enum)


   .. py:attribute:: device_and_sensor_status
      :type:  PLXDeviceAndSensorStatus | None
      :value: None



   .. py:attribute:: measurement_status
      :type:  PLXMeasurementStatus | None
      :value: None



   .. py:attribute:: pulse_amplitude_index
      :type:  float | None
      :value: None



   .. py:attribute:: pulse_rate
      :type:  float


   .. py:attribute:: spo2
      :type:  float


   .. py:attribute:: spot_check_flags
      :type:  PLXSpotCheckFlags


   .. py:attribute:: supported_features
      :type:  src.bluetooth_sig.gatt.characteristics.plx_features.PLXFeatureFlags | None
      :value: None



.. py:class:: PLXSpotCheckFlags

   Bases: :py:obj:`enum.IntFlag`


   PLX Spot-Check measurement flags.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: DEVICE_AND_SENSOR_STATUS_PRESENT
      :value: 4



   .. py:attribute:: MEASUREMENT_STATUS_PRESENT
      :value: 2



   .. py:attribute:: PULSE_AMPLITUDE_INDEX_PRESENT
      :value: 8



   .. py:attribute:: SPO2PR_FAST
      :value: 1



.. py:class:: PLXSpotCheckMeasurementCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   PLX Spot-Check Measurement characteristic (0x2A5E).

   Used to transmit single SpO2 (blood oxygen saturation) and pulse rate
   measurements from spot-check readings.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> PLXSpotCheckData

      Parse PLX spot-check measurement data according to Bluetooth specification.

      Format: Flags(1) + SpO2(2) + Pulse Rate(2) + [Measurement Status(2)] +
      [Device and Sensor Status(3)] + [Pulse Amplitude Index(2)]
      SpO2 and Pulse Rate are IEEE-11073 16-bit SFLOAT.

      Context Enhancement:
          If ctx is provided, this method will attempt to enhance the parsed data with:
          - PLX Features (0x2A60): Device capabilities and supported measurement types

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: PLXSpotCheckData containing parsed PLX spot-check data with optional
                context-enhanced information.



   .. py:method:: encode_value(data: PLXSpotCheckData) -> bytearray

      Encode PLX spot-check measurement value back to bytes.

      :param data: PLXSpotCheckData instance to encode

      :returns: Encoded bytes representing the measurement



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: True



   .. py:attribute:: max_length
      :type:  int | None
      :value: 12



   .. py:attribute:: min_length
      :type:  int | None
      :value: 5



.. py:data:: logger

