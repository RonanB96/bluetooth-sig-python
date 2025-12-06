src.bluetooth_sig.gatt.characteristics.weight_scale_feature
===========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.weight_scale_feature

.. autoapi-nested-parse::

   Weight Scale Feature characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.weight_scale_feature.HeightMeasurementResolution
   src.bluetooth_sig.gatt.characteristics.weight_scale_feature.WeightMeasurementResolution
   src.bluetooth_sig.gatt.characteristics.weight_scale_feature.WeightScaleBits
   src.bluetooth_sig.gatt.characteristics.weight_scale_feature.WeightScaleFeatureCharacteristic
   src.bluetooth_sig.gatt.characteristics.weight_scale_feature.WeightScaleFeatureData
   src.bluetooth_sig.gatt.characteristics.weight_scale_feature.WeightScaleFeatures


Module Contents
---------------

.. py:class:: HeightMeasurementResolution

   Bases: :py:obj:`enum.IntEnum`


   Height measurement resolution enumeration.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: NOT_SPECIFIED
      :value: 0



   .. py:attribute:: POINT_001_M_OR_POINT_1_INCH
      :value: 3



   .. py:attribute:: POINT_005_M_OR_HALF_INCH
      :value: 2



   .. py:attribute:: POINT_01_M_OR_1_INCH
      :value: 1



.. py:class:: WeightMeasurementResolution

   Bases: :py:obj:`enum.IntEnum`


   Weight measurement resolution enumeration.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: HALF_KG_OR_1_LB
      :value: 1



   .. py:attribute:: NOT_SPECIFIED
      :value: 0



   .. py:attribute:: POINT_005_KG_OR_POINT_01_LB
      :value: 7



   .. py:attribute:: POINT_01_KG_OR_POINT_02_LB
      :value: 6



   .. py:attribute:: POINT_02_KG_OR_POINT_05_LB
      :value: 5



   .. py:attribute:: POINT_05_KG_OR_POINT_1_LB
      :value: 4



   .. py:attribute:: POINT_1_KG_OR_POINT_2_LB
      :value: 3



   .. py:attribute:: POINT_2_KG_OR_HALF_LB
      :value: 2



.. py:class:: WeightScaleBits

   Weight scale bit field constants.


   .. py:attribute:: HEIGHT_RESOLUTION_BIT_WIDTH
      :value: 3



   .. py:attribute:: HEIGHT_RESOLUTION_START_BIT
      :value: 7



   .. py:attribute:: WEIGHT_RESOLUTION_BIT_WIDTH
      :value: 4



   .. py:attribute:: WEIGHT_RESOLUTION_START_BIT
      :value: 3



.. py:class:: WeightScaleFeatureCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Weight Scale Feature characteristic (0x2A9E).

   Used to indicate which optional features are supported by the weight
   scale. This is a read-only characteristic that describes device
   capabilities.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> WeightScaleFeatureData

      Parse weight scale feature data according to Bluetooth specification.

      Format: Features(4 bytes) - bitmask indicating supported features.

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: WeightScaleFeatureData containing parsed feature flags.

      :raises ValueError: If data format is invalid.



   .. py:method:: encode_value(data: WeightScaleFeatureData) -> bytearray

      Encode weight scale feature value back to bytes.

      :param data: WeightScaleFeatureData with feature flags

      :returns: Encoded bytes representing the weight scale features (uint32)



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: False



   .. py:attribute:: max_length
      :type:  int
      :value: 4



   .. py:attribute:: min_length
      :type:  int
      :value: 4



.. py:class:: WeightScaleFeatureData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Weight Scale Feature characteristic.


   .. py:attribute:: bmi_supported
      :type:  bool


   .. py:attribute:: height_measurement_resolution
      :type:  HeightMeasurementResolution


   .. py:attribute:: multiple_users_supported
      :type:  bool


   .. py:attribute:: raw_value
      :type:  int


   .. py:attribute:: timestamp_supported
      :type:  bool


   .. py:attribute:: weight_measurement_resolution
      :type:  WeightMeasurementResolution


.. py:class:: WeightScaleFeatures

   Bases: :py:obj:`enum.IntFlag`


   Weight Scale Feature flags as per Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: BMI_SUPPORTED
      :value: 4



   .. py:attribute:: MULTIPLE_USERS_SUPPORTED
      :value: 2



   .. py:attribute:: TIMESTAMP_SUPPORTED
      :value: 1



