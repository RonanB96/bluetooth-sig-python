src.bluetooth_sig.gatt.characteristics.blood_pressure_feature
=============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.blood_pressure_feature

.. autoapi-nested-parse::

   Blood Pressure Feature characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.blood_pressure_feature.BloodPressureFeatureCharacteristic
   src.bluetooth_sig.gatt.characteristics.blood_pressure_feature.BloodPressureFeatureData
   src.bluetooth_sig.gatt.characteristics.blood_pressure_feature.BloodPressureFeatures


Module Contents
---------------

.. py:class:: BloodPressureFeatureCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Blood Pressure Feature characteristic (0x2A49).

   Used to expose the supported features of a blood pressure monitoring
   device. Indicates which optional measurements and capabilities are
   available.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> BloodPressureFeatureData

      Parse blood pressure feature data according to Bluetooth specification.

      Format: Features(2) - 16-bit bitmap indicating supported features.

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: BloodPressureFeatureData containing parsed feature bitmap and capabilities.



   .. py:method:: encode_value(data: BloodPressureFeatureData) -> bytearray

      Encode BloodPressureFeatureData back to bytes.

      :param data: BloodPressureFeatureData instance to encode

      :returns: Encoded bytes representing the blood pressure features



.. py:class:: BloodPressureFeatureData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Blood Pressure Feature characteristic.


   .. py:attribute:: body_movement_detection_support
      :type:  bool


   .. py:attribute:: cuff_fit_detection_support
      :type:  bool


   .. py:attribute:: features_bitmap
      :type:  int


   .. py:attribute:: irregular_pulse_detection_support
      :type:  bool


   .. py:attribute:: measurement_position_detection_support
      :type:  bool


   .. py:attribute:: multiple_bond_support
      :type:  bool


   .. py:attribute:: pulse_rate_range_detection_support
      :type:  bool


.. py:class:: BloodPressureFeatures

   Bases: :py:obj:`enum.IntFlag`


   Blood Pressure Feature flags as per Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: BODY_MOVEMENT_DETECTION
      :value: 1



   .. py:attribute:: CUFF_FIT_DETECTION
      :value: 2



   .. py:attribute:: IRREGULAR_PULSE_DETECTION
      :value: 4



   .. py:attribute:: MEASUREMENT_POSITION_DETECTION
      :value: 16



   .. py:attribute:: MULTIPLE_BOND_SUPPORT
      :value: 32



   .. py:attribute:: PULSE_RATE_RANGE_DETECTION
      :value: 8



