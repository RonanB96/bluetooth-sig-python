src.bluetooth_sig.gatt.characteristics.glucose_measurement_context
==================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.glucose_measurement_context

.. autoapi-nested-parse::

   Glucose Measurement Context characteristic implementation.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.logger


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.ExtendedFlagsResult
   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.CarbohydrateResult
   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.MealResult
   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.TesterHealthResult
   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.ExerciseResult
   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.MedicationResult
   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.GlucoseMeasurementContextBits
   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.CarbohydrateType
   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.MealType
   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.GlucoseTester
   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.HealthType
   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.MedicationType
   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.GlucoseMeasurementContextExtendedFlags
   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.GlucoseMeasurementContextFlags
   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.GlucoseMeasurementContextData
   src.bluetooth_sig.gatt.characteristics.glucose_measurement_context.GlucoseMeasurementContextCharacteristic


Module Contents
---------------

.. py:data:: logger

.. py:class:: ExtendedFlagsResult

   Bases: :py:obj:`msgspec.Struct`


   Extended flags parsing result.


   .. py:attribute:: extended_flags
      :type:  int | None


   .. py:attribute:: offset
      :type:  int


.. py:class:: CarbohydrateResult

   Bases: :py:obj:`msgspec.Struct`


   Carbohydrate information parsing result.


   .. py:attribute:: carbohydrate_id
      :type:  CarbohydrateType | None


   .. py:attribute:: carbohydrate_kg
      :type:  float | None


   .. py:attribute:: offset
      :type:  int


.. py:class:: MealResult

   Bases: :py:obj:`msgspec.Struct`


   Meal information parsing result.


   .. py:attribute:: meal
      :type:  MealType | None


   .. py:attribute:: offset
      :type:  int


.. py:class:: TesterHealthResult

   Bases: :py:obj:`msgspec.Struct`


   Tester and health information parsing result.


   .. py:attribute:: tester
      :type:  GlucoseTester | None


   .. py:attribute:: health
      :type:  HealthType | None


   .. py:attribute:: offset
      :type:  int


.. py:class:: ExerciseResult

   Bases: :py:obj:`msgspec.Struct`


   Exercise information parsing result.


   .. py:attribute:: exercise_duration_seconds
      :type:  int | None


   .. py:attribute:: exercise_intensity_percent
      :type:  int | None


   .. py:attribute:: offset
      :type:  int


.. py:class:: MedicationResult

   Bases: :py:obj:`msgspec.Struct`


   Medication information parsing result.


   .. py:attribute:: medication_id
      :type:  MedicationType | None


   .. py:attribute:: medication_kg
      :type:  float | None


   .. py:attribute:: offset
      :type:  int


.. py:class:: GlucoseMeasurementContextBits

   Glucose Measurement Context bit field constants.


   .. py:attribute:: TESTER_START_BIT
      :value: 4



   .. py:attribute:: TESTER_BIT_WIDTH
      :value: 4



   .. py:attribute:: HEALTH_START_BIT
      :value: 0



   .. py:attribute:: HEALTH_BIT_WIDTH
      :value: 4



.. py:class:: CarbohydrateType

   Bases: :py:obj:`enum.IntEnum`


   Carbohydrate type enumeration as per Bluetooth SIG specification.


   .. py:attribute:: BREAKFAST
      :value: 1



   .. py:attribute:: LUNCH
      :value: 2



   .. py:attribute:: DINNER
      :value: 3



   .. py:attribute:: SNACK
      :value: 4



   .. py:attribute:: DRINK
      :value: 5



   .. py:attribute:: SUPPER
      :value: 6



   .. py:attribute:: BRUNCH
      :value: 7



.. py:class:: MealType

   Bases: :py:obj:`enum.IntEnum`


   Meal type enumeration as per Bluetooth SIG specification.


   .. py:attribute:: PREPRANDIAL
      :value: 1



   .. py:attribute:: POSTPRANDIAL
      :value: 2



   .. py:attribute:: FASTING
      :value: 3



   .. py:attribute:: CASUAL
      :value: 4



   .. py:attribute:: BEDTIME
      :value: 5



.. py:class:: GlucoseTester

   Bases: :py:obj:`enum.IntEnum`


   Glucose tester type enumeration as per Bluetooth SIG specification.


   .. py:attribute:: SELF
      :value: 1



   .. py:attribute:: HEALTH_CARE_PROFESSIONAL
      :value: 2



   .. py:attribute:: LAB_TEST
      :value: 3



   .. py:attribute:: NOT_AVAILABLE
      :value: 15



.. py:class:: HealthType

   Bases: :py:obj:`enum.IntEnum`


   Health type enumeration as per Bluetooth SIG specification.


   .. py:attribute:: MINOR_HEALTH_ISSUES
      :value: 1



   .. py:attribute:: MAJOR_HEALTH_ISSUES
      :value: 2



   .. py:attribute:: DURING_MENSES
      :value: 3



   .. py:attribute:: UNDER_STRESS
      :value: 4



   .. py:attribute:: NO_HEALTH_ISSUES
      :value: 5



   .. py:attribute:: NOT_AVAILABLE
      :value: 15



.. py:class:: MedicationType

   Bases: :py:obj:`enum.IntEnum`


   Medication type enumeration as per Bluetooth SIG specification.


   .. py:attribute:: RAPID_ACTING_INSULIN
      :value: 1



   .. py:attribute:: SHORT_ACTING_INSULIN
      :value: 2



   .. py:attribute:: INTERMEDIATE_ACTING_INSULIN
      :value: 3



   .. py:attribute:: LONG_ACTING_INSULIN
      :value: 4



   .. py:attribute:: PRE_MIXED_INSULIN
      :value: 5



.. py:class:: GlucoseMeasurementContextExtendedFlags

   Bases: :py:obj:`enum.IntEnum`


   Glucose Measurement Context Extended Flags constants as per Bluetooth SIG specification.

   Currently all bits are reserved for future use.


   .. py:attribute:: RESERVED_BIT_0
      :value: 1



   .. py:attribute:: RESERVED_BIT_1
      :value: 2



   .. py:attribute:: RESERVED_BIT_2
      :value: 4



   .. py:attribute:: RESERVED_BIT_3
      :value: 8



   .. py:attribute:: RESERVED_BIT_4
      :value: 16



   .. py:attribute:: RESERVED_BIT_5
      :value: 32



   .. py:attribute:: RESERVED_BIT_6
      :value: 64



   .. py:attribute:: RESERVED_BIT_7
      :value: 128



   .. py:method:: get_description(flags: int) -> str
      :staticmethod:


      Get description of extended flags.

      :param flags: Extended flags value (0-255)

      :returns: Description string indicating all bits are reserved



.. py:class:: GlucoseMeasurementContextFlags

   Bases: :py:obj:`enum.IntFlag`


   Glucose Measurement Context flags as per Bluetooth SIG specification.


   .. py:attribute:: EXTENDED_FLAGS_PRESENT
      :value: 1



   .. py:attribute:: CARBOHYDRATE_PRESENT
      :value: 2



   .. py:attribute:: MEAL_PRESENT
      :value: 4



   .. py:attribute:: TESTER_HEALTH_PRESENT
      :value: 8



   .. py:attribute:: EXERCISE_PRESENT
      :value: 16



   .. py:attribute:: MEDICATION_PRESENT
      :value: 32



   .. py:attribute:: HBA1C_PRESENT
      :value: 64



   .. py:attribute:: RESERVED
      :value: 128



.. py:class:: GlucoseMeasurementContextData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Glucose Measurement Context characteristic.

   Used for both parsing and encoding - None values represent optional fields.


   .. py:attribute:: sequence_number
      :type:  int


   .. py:attribute:: flags
      :type:  GlucoseMeasurementContextFlags


   .. py:attribute:: extended_flags
      :type:  int | None
      :value: None



   .. py:attribute:: carbohydrate_id
      :type:  CarbohydrateType | None
      :value: None



   .. py:attribute:: carbohydrate_kg
      :type:  float | None
      :value: None



   .. py:attribute:: meal
      :type:  MealType | None
      :value: None



   .. py:attribute:: tester
      :type:  GlucoseTester | None
      :value: None



   .. py:attribute:: health
      :type:  HealthType | None
      :value: None



   .. py:attribute:: exercise_duration_seconds
      :type:  int | None
      :value: None



   .. py:attribute:: exercise_intensity_percent
      :type:  int | None
      :value: None



   .. py:attribute:: medication_id
      :type:  MedicationType | None
      :value: None



   .. py:attribute:: medication_kg
      :type:  float | None
      :value: None



   .. py:attribute:: hba1c_percent
      :type:  float | None
      :value: None



.. py:class:: GlucoseMeasurementContextCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Glucose Measurement Context characteristic (0x2A34).

   Used to transmit additional context for glucose measurements
   including carbohydrate intake, exercise, medication, and HbA1c
   information.

   SIG Specification Pattern:
   This characteristic depends on Glucose Measurement (0x2A18) for sequence number
   matching. The sequence_number field in this context must match the sequence_number
   from a corresponding Glucose Measurement characteristic.


   .. py:attribute:: min_length
      :type:  int | None
      :value: 3



   .. py:attribute:: max_length
      :type:  int | None
      :value: 19



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: True



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> GlucoseMeasurementContextData

      Parse glucose measurement context data according to Bluetooth specification.

      Format: Flags(1) + Sequence Number(2) + [Extended Flags(1)] + [Carbohydrate ID(1) + Carb(2)] +
              [Meal(1)] + [Tester-Health(1)] + [Exercise Duration(2) + Exercise Intensity(1)] +
              [Medication ID(1) + Medication(2)] + [HbA1c(2)].

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional context providing access to Glucose Measurement characteristic
                  for sequence number validation.

      :returns: GlucoseMeasurementContextData containing parsed glucose context data.

      :raises ValueError: If data format is invalid.

      SIG Pattern:
      When context is available, validates that this context's sequence_number matches
      a Glucose Measurement sequence_number, following the SIG specification pattern
      where contexts are paired with measurements via sequence number matching.




   .. py:method:: encode_value(data: GlucoseMeasurementContextData) -> bytearray

      Encode glucose measurement context value back to bytes.

      :param data: GlucoseMeasurementContextData containing glucose measurement context data

      :returns: Encoded bytes representing the measurement context



