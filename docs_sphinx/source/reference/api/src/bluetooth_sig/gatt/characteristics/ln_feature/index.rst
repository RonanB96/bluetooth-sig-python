src.bluetooth_sig.gatt.characteristics.ln_feature
=================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.ln_feature

.. autoapi-nested-parse::

   LN Feature characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.ln_feature.LNFeatures
   src.bluetooth_sig.gatt.characteristics.ln_feature.LNFeatureData
   src.bluetooth_sig.gatt.characteristics.ln_feature.LNFeatureCharacteristic


Module Contents
---------------

.. py:class:: LNFeatures

   Bases: :py:obj:`enum.IntFlag`


   LN Feature flags as per Bluetooth SIG specification.


   .. py:attribute:: INSTANTANEOUS_SPEED_SUPPORTED
      :value: 1



   .. py:attribute:: TOTAL_DISTANCE_SUPPORTED
      :value: 2



   .. py:attribute:: LOCATION_SUPPORTED
      :value: 4



   .. py:attribute:: ELEVATION_SUPPORTED
      :value: 8



   .. py:attribute:: HEADING_SUPPORTED
      :value: 16



   .. py:attribute:: ROLLING_TIME_SUPPORTED
      :value: 32



   .. py:attribute:: UTC_TIME_SUPPORTED
      :value: 64



   .. py:attribute:: REMAINING_DISTANCE_SUPPORTED
      :value: 128



   .. py:attribute:: REMAINING_VERTICAL_DISTANCE_SUPPORTED
      :value: 256



   .. py:attribute:: ESTIMATED_TIME_OF_ARRIVAL_SUPPORTED
      :value: 512



   .. py:attribute:: NUMBER_OF_BEACONS_IN_SOLUTION_SUPPORTED
      :value: 1024



   .. py:attribute:: NUMBER_OF_BEACONS_IN_VIEW_SUPPORTED
      :value: 2048



   .. py:attribute:: TIME_TO_FIRST_FIX_SUPPORTED
      :value: 4096



   .. py:attribute:: ESTIMATED_HORIZONTAL_POSITION_ERROR_SUPPORTED
      :value: 8192



   .. py:attribute:: ESTIMATED_VERTICAL_POSITION_ERROR_SUPPORTED
      :value: 16384



   .. py:attribute:: HORIZONTAL_DILUTION_OF_PRECISION_SUPPORTED
      :value: 32768



   .. py:attribute:: VERTICAL_DILUTION_OF_PRECISION_SUPPORTED
      :value: 65536



   .. py:attribute:: LOCATION_AND_SPEED_CHARACTERISTIC_CONTENT_MASKING_SUPPORTED
      :value: 131072



   .. py:attribute:: FIX_RATE_SETTING_SUPPORTED
      :value: 262144



   .. py:attribute:: ELEVATION_SETTING_SUPPORTED
      :value: 524288



   .. py:attribute:: POSITION_STATUS_SUPPORTED
      :value: 1048576



.. py:class:: LNFeatureData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from LN Feature characteristic.


   .. py:attribute:: features_bitmap
      :type:  int


   .. py:attribute:: instantaneous_speed_supported
      :type:  bool


   .. py:attribute:: total_distance_supported
      :type:  bool


   .. py:attribute:: location_supported
      :type:  bool


   .. py:attribute:: elevation_supported
      :type:  bool


   .. py:attribute:: heading_supported
      :type:  bool


   .. py:attribute:: rolling_time_supported
      :type:  bool


   .. py:attribute:: utc_time_supported
      :type:  bool


   .. py:attribute:: remaining_distance_supported
      :type:  bool


   .. py:attribute:: remaining_vertical_distance_supported
      :type:  bool


   .. py:attribute:: estimated_time_of_arrival_supported
      :type:  bool


   .. py:attribute:: number_of_beacons_in_solution_supported
      :type:  bool


   .. py:attribute:: number_of_beacons_in_view_supported
      :type:  bool


   .. py:attribute:: time_to_first_fix_supported
      :type:  bool


   .. py:attribute:: estimated_horizontal_position_error_supported
      :type:  bool


   .. py:attribute:: estimated_vertical_position_error_supported
      :type:  bool


   .. py:attribute:: horizontal_dilution_of_precision_supported
      :type:  bool


   .. py:attribute:: vertical_dilution_of_precision_supported
      :type:  bool


   .. py:attribute:: location_and_speed_characteristic_content_masking_supported
      :type:  bool


   .. py:attribute:: fix_rate_setting_supported
      :type:  bool


   .. py:attribute:: elevation_setting_supported
      :type:  bool


   .. py:attribute:: position_status_supported
      :type:  bool


.. py:class:: LNFeatureCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   LN Feature characteristic.

   Used to represent the supported features of a location and navigation sensor.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> LNFeatureData

      Parse LN feature data according to Bluetooth specification.

      Format: Features(4) - 32-bit bitmap indicating supported features.

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: LNFeatureData containing parsed feature bitmap and capabilities.



   .. py:method:: encode_value(data: LNFeatureData) -> bytearray

      Encode LNFeatureData back to bytes.

      :param data: LNFeatureData instance to encode

      :returns: Encoded bytes representing the LN features



