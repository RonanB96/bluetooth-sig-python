src.bluetooth_sig.gatt.characteristics.body_composition_feature
===============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.body_composition_feature

.. autoapi-nested-parse::

   Body Composition Feature characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.body_composition_feature.BodyCompositionFeatureBits
   src.bluetooth_sig.gatt.characteristics.body_composition_feature.MassMeasurementResolution
   src.bluetooth_sig.gatt.characteristics.body_composition_feature.HeightMeasurementResolution
   src.bluetooth_sig.gatt.characteristics.body_composition_feature.BodyCompositionFeatures
   src.bluetooth_sig.gatt.characteristics.body_composition_feature.BodyCompositionFeatureData
   src.bluetooth_sig.gatt.characteristics.body_composition_feature.BodyCompositionFeatureCharacteristic


Module Contents
---------------

.. py:class:: BodyCompositionFeatureBits

   Body Composition Feature bit field constants.


   .. py:attribute:: MASS_RESOLUTION_START_BIT
      :value: 11



   .. py:attribute:: MASS_RESOLUTION_BIT_WIDTH
      :value: 4



   .. py:attribute:: HEIGHT_RESOLUTION_START_BIT
      :value: 15



   .. py:attribute:: HEIGHT_RESOLUTION_BIT_WIDTH
      :value: 3



.. py:class:: MassMeasurementResolution

   Bases: :py:obj:`enum.IntEnum`


   Mass measurement resolution enumeration.


   .. py:attribute:: NOT_SPECIFIED
      :value: 0



   .. py:attribute:: KG_0_5_OR_LB_1
      :value: 1



   .. py:attribute:: KG_0_2_OR_LB_0_5
      :value: 2



   .. py:attribute:: KG_0_1_OR_LB_0_2
      :value: 3



   .. py:attribute:: KG_0_05_OR_LB_0_1
      :value: 4



   .. py:attribute:: KG_0_02_OR_LB_0_05
      :value: 5



   .. py:attribute:: KG_0_01_OR_LB_0_02
      :value: 6



   .. py:attribute:: KG_0_005_OR_LB_0_01
      :value: 7



.. py:class:: HeightMeasurementResolution

   Bases: :py:obj:`enum.IntEnum`


   Height measurement resolution enumeration.


   .. py:attribute:: NOT_SPECIFIED
      :value: 0



   .. py:attribute:: M_0_01_OR_INCH_1
      :value: 1



   .. py:attribute:: M_0_005_OR_INCH_0_5
      :value: 2



   .. py:attribute:: M_0_001_OR_INCH_0_1
      :value: 3



.. py:class:: BodyCompositionFeatures

   Bases: :py:obj:`enum.IntFlag`


   Body Composition Feature flags as per Bluetooth SIG specification.


   .. py:attribute:: TIMESTAMP_SUPPORTED
      :value: 1



   .. py:attribute:: MULTIPLE_USERS_SUPPORTED
      :value: 2



   .. py:attribute:: BASAL_METABOLISM_SUPPORTED
      :value: 4



   .. py:attribute:: MUSCLE_MASS_SUPPORTED
      :value: 8



   .. py:attribute:: MUSCLE_PERCENTAGE_SUPPORTED
      :value: 16



   .. py:attribute:: FAT_FREE_MASS_SUPPORTED
      :value: 32



   .. py:attribute:: SOFT_LEAN_MASS_SUPPORTED
      :value: 64



   .. py:attribute:: BODY_WATER_MASS_SUPPORTED
      :value: 128



   .. py:attribute:: IMPEDANCE_SUPPORTED
      :value: 256



   .. py:attribute:: WEIGHT_SUPPORTED
      :value: 512



   .. py:attribute:: HEIGHT_SUPPORTED
      :value: 1024



.. py:class:: BodyCompositionFeatureData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Body Composition Feature characteristic.


   .. py:attribute:: features
      :type:  BodyCompositionFeatures


   .. py:attribute:: timestamp_supported
      :type:  bool


   .. py:attribute:: multiple_users_supported
      :type:  bool


   .. py:attribute:: basal_metabolism_supported
      :type:  bool


   .. py:attribute:: muscle_mass_supported
      :type:  bool


   .. py:attribute:: muscle_percentage_supported
      :type:  bool


   .. py:attribute:: fat_free_mass_supported
      :type:  bool


   .. py:attribute:: soft_lean_mass_supported
      :type:  bool


   .. py:attribute:: body_water_mass_supported
      :type:  bool


   .. py:attribute:: impedance_supported
      :type:  bool


   .. py:attribute:: weight_supported
      :type:  bool


   .. py:attribute:: height_supported
      :type:  bool


   .. py:attribute:: mass_measurement_resolution
      :type:  MassMeasurementResolution


   .. py:attribute:: height_measurement_resolution
      :type:  HeightMeasurementResolution


.. py:class:: BodyCompositionFeatureCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Body Composition Feature characteristic (0x2A9B).

   Used to indicate which optional features and measurements are
   supported by the body composition device. This is a read-only
   characteristic that describes device capabilities.


   .. py:attribute:: min_length
      :type:  int
      :value: 4



   .. py:attribute:: max_length
      :type:  int
      :value: 4



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: False



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> BodyCompositionFeatureData

      Parse body composition feature data according to Bluetooth specification.

      Format: Features(4 bytes) - bitmask indicating supported measurements.

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: BodyCompositionFeatureData containing parsed feature flags.

      :raises ValueError: If data format is invalid.



   .. py:method:: encode_value(data: BodyCompositionFeatureData) -> bytearray

      Encode BodyCompositionFeatureData back to bytes.

      :param data: BodyCompositionFeatureData instance to encode

      :returns: Encoded bytes representing the body composition features



