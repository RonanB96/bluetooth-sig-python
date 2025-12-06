src.bluetooth_sig.gatt.characteristics.glucose_feature
======================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.glucose_feature

.. autoapi-nested-parse::

   Glucose Feature characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.glucose_feature.GlucoseFeatureCharacteristic
   src.bluetooth_sig.gatt.characteristics.glucose_feature.GlucoseFeatureData
   src.bluetooth_sig.gatt.characteristics.glucose_feature.GlucoseFeatures


Module Contents
---------------

.. py:class:: GlucoseFeatureCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Glucose Feature characteristic (0x2A51).

   Used to expose the supported features of a glucose monitoring
   device. Indicates which optional fields and capabilities are
   available.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> GlucoseFeatureData

      Parse glucose feature data according to Bluetooth specification.

      Format: Features(2) - 16-bit bitmap indicating supported features

      :param data: Raw bytearray from BLE characteristic
      :param ctx: Optional context information

      :returns: GlucoseFeatureData containing parsed feature bitmap and details

      :raises ValueError: If data format is invalid



   .. py:method:: encode_value(data: GlucoseFeatureData) -> bytearray

      Encode GlucoseFeatureData back to bytes.

      :param data: GlucoseFeatureData instance to encode

      :returns: Encoded bytes representing the glucose features



   .. py:method:: get_feature_description(feature_bit: int) -> str

      Get description for a specific feature bit.

      :param feature_bit: Bit position (0-15)

      :returns: Human-readable description of the feature



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: False



   .. py:attribute:: max_length
      :type:  int
      :value: 2



   .. py:attribute:: min_length
      :type:  int
      :value: 2



.. py:class:: GlucoseFeatureData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Glucose Feature characteristic.


   .. py:attribute:: enabled_features
      :type:  tuple[GlucoseFeatures, Ellipsis]


   .. py:attribute:: feature_count
      :type:  int


   .. py:attribute:: features_bitmap
      :type:  GlucoseFeatures


   .. py:attribute:: general_device_fault
      :type:  bool


   .. py:attribute:: low_battery_detection
      :type:  bool


   .. py:attribute:: multiple_bond_support
      :type:  bool


   .. py:attribute:: sensor_malfunction_detection
      :type:  bool


   .. py:attribute:: sensor_read_interrupt
      :type:  bool


   .. py:attribute:: sensor_result_high_low
      :type:  bool


   .. py:attribute:: sensor_sample_size
      :type:  bool


   .. py:attribute:: sensor_strip_insertion_error
      :type:  bool


   .. py:attribute:: sensor_strip_type_error
      :type:  bool


   .. py:attribute:: sensor_temperature_high_low
      :type:  bool


   .. py:attribute:: time_fault
      :type:  bool


.. py:class:: GlucoseFeatures

   Bases: :py:obj:`enum.IntFlag`


   Glucose Feature flags according to Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:method:: get_enabled_features() -> list[GlucoseFeatures]

      Get list of human-readable enabled features.



   .. py:attribute:: GENERAL_DEVICE_FAULT
      :value: 256



   .. py:attribute:: LOW_BATTERY_DETECTION
      :value: 1



   .. py:attribute:: MULTIPLE_BOND_SUPPORT
      :value: 1024



   .. py:attribute:: SENSOR_MALFUNCTION_DETECTION
      :value: 2



   .. py:attribute:: SENSOR_READ_INTERRUPT
      :value: 128



   .. py:attribute:: SENSOR_RESULT_HIGH_LOW
      :value: 32



   .. py:attribute:: SENSOR_SAMPLE_SIZE
      :value: 4



   .. py:attribute:: SENSOR_STRIP_INSERTION_ERROR
      :value: 8



   .. py:attribute:: SENSOR_STRIP_TYPE_ERROR
      :value: 16



   .. py:attribute:: SENSOR_TEMPERATURE_HIGH_LOW
      :value: 64



   .. py:attribute:: TIME_FAULT
      :value: 512



