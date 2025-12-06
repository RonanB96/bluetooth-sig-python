src.bluetooth_sig.gatt.characteristics.body_composition_measurement
===================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.body_composition_measurement

.. autoapi-nested-parse::

   Body Composition Measurement characteristic implementation.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.body_composition_measurement.BODY_FAT_PERCENTAGE_RESOLUTION
   src.bluetooth_sig.gatt.characteristics.body_composition_measurement.HEIGHT_RESOLUTION_IMPERIAL
   src.bluetooth_sig.gatt.characteristics.body_composition_measurement.HEIGHT_RESOLUTION_METRIC
   src.bluetooth_sig.gatt.characteristics.body_composition_measurement.IMPEDANCE_RESOLUTION
   src.bluetooth_sig.gatt.characteristics.body_composition_measurement.MASS_RESOLUTION_KG
   src.bluetooth_sig.gatt.characteristics.body_composition_measurement.MASS_RESOLUTION_LB
   src.bluetooth_sig.gatt.characteristics.body_composition_measurement.MUSCLE_PERCENTAGE_RESOLUTION


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.body_composition_measurement.BasicOptionalFields
   src.bluetooth_sig.gatt.characteristics.body_composition_measurement.BodyCompositionFlags
   src.bluetooth_sig.gatt.characteristics.body_composition_measurement.BodyCompositionMeasurementCharacteristic
   src.bluetooth_sig.gatt.characteristics.body_composition_measurement.BodyCompositionMeasurementData
   src.bluetooth_sig.gatt.characteristics.body_composition_measurement.FlagsAndBodyFat
   src.bluetooth_sig.gatt.characteristics.body_composition_measurement.MassFields
   src.bluetooth_sig.gatt.characteristics.body_composition_measurement.MassValue
   src.bluetooth_sig.gatt.characteristics.body_composition_measurement.OtherMeasurements


Module Contents
---------------

.. py:class:: BasicOptionalFields

   Bases: :py:obj:`msgspec.Struct`


   Basic optional fields: timestamp, user ID, and basal metabolism.


   .. py:attribute:: basal_metabolism
      :type:  int | None


   .. py:attribute:: offset
      :type:  int


   .. py:attribute:: timestamp
      :type:  datetime.datetime | None


   .. py:attribute:: user_id
      :type:  int | None


.. py:class:: BodyCompositionFlags

   Bases: :py:obj:`enum.IntFlag`


   Body Composition Measurement flags as per Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: BASAL_METABOLISM_PRESENT
      :value: 8



   .. py:attribute:: BODY_WATER_MASS_PRESENT
      :value: 256



   .. py:attribute:: FAT_FREE_MASS_PRESENT
      :value: 64



   .. py:attribute:: HEIGHT_PRESENT
      :value: 2048



   .. py:attribute:: IMPEDANCE_PRESENT
      :value: 512



   .. py:attribute:: IMPERIAL_UNITS
      :value: 1



   .. py:attribute:: MUSCLE_MASS_PRESENT
      :value: 16



   .. py:attribute:: MUSCLE_PERCENTAGE_PRESENT
      :value: 32



   .. py:attribute:: SOFT_LEAN_MASS_PRESENT
      :value: 128



   .. py:attribute:: TIMESTAMP_PRESENT
      :value: 2



   .. py:attribute:: USER_ID_PRESENT
      :value: 4



   .. py:attribute:: WEIGHT_PRESENT
      :value: 1024



.. py:class:: BodyCompositionMeasurementCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Body Composition Measurement characteristic (0x2A9C).

   Used to transmit body composition measurement data including body
   fat percentage, muscle mass, bone mass, water percentage, and other
   body metrics.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> BodyCompositionMeasurementData

      Parse body composition measurement data according to Bluetooth specification.

      Format: Flags(2) + Body Fat %(2) + [Timestamp(7)] + [User ID(1)] +
              [Basal Metabolism(2)] + [Muscle Mass(2)] + [etc...]

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: BodyCompositionMeasurementData containing parsed body composition data.

      :raises ValueError: If data format is invalid.



   .. py:method:: encode_value(data: BodyCompositionMeasurementData) -> bytearray

      Encode body composition measurement value back to bytes.

      :param data: BodyCompositionMeasurementData containing body composition measurement data

      :returns: Encoded bytes representing the measurement



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: True



   .. py:attribute:: max_length
      :type:  int
      :value: 50



   .. py:attribute:: min_length
      :type:  int
      :value: 4



.. py:class:: BodyCompositionMeasurementData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Body Composition Measurement characteristic.


   .. py:attribute:: basal_metabolism
      :type:  int | None
      :value: None



   .. py:attribute:: body_fat_percentage
      :type:  float


   .. py:attribute:: body_water_mass
      :type:  float | None
      :value: None



   .. py:attribute:: fat_free_mass
      :type:  float | None
      :value: None



   .. py:attribute:: flags
      :type:  BodyCompositionFlags


   .. py:attribute:: height
      :type:  float | None
      :value: None



   .. py:attribute:: impedance
      :type:  float | None
      :value: None



   .. py:attribute:: measurement_units
      :type:  bluetooth_sig.types.units.MeasurementSystem


   .. py:attribute:: muscle_mass
      :type:  float | None
      :value: None



   .. py:attribute:: muscle_mass_unit
      :type:  bluetooth_sig.types.units.WeightUnit | None
      :value: None



   .. py:attribute:: muscle_percentage
      :type:  float | None
      :value: None



   .. py:attribute:: soft_lean_mass
      :type:  float | None
      :value: None



   .. py:attribute:: timestamp
      :type:  datetime.datetime | None
      :value: None



   .. py:attribute:: user_id
      :type:  int | None
      :value: None



   .. py:attribute:: weight
      :type:  float | None
      :value: None



.. py:class:: FlagsAndBodyFat

   Bases: :py:obj:`msgspec.Struct`


   Flags and body fat percentage with parsing offset.


   .. py:attribute:: body_fat_percentage
      :type:  float


   .. py:attribute:: flags
      :type:  BodyCompositionFlags


   .. py:attribute:: offset
      :type:  int


.. py:class:: MassFields

   Bases: :py:obj:`msgspec.Struct`


   Mass-related optional fields.


   .. py:attribute:: body_water_mass
      :type:  float | None


   .. py:attribute:: fat_free_mass
      :type:  float | None


   .. py:attribute:: muscle_mass
      :type:  float | None


   .. py:attribute:: muscle_mass_unit
      :type:  bluetooth_sig.types.units.WeightUnit | None


   .. py:attribute:: muscle_percentage
      :type:  float | None


   .. py:attribute:: offset
      :type:  int


   .. py:attribute:: soft_lean_mass
      :type:  float | None


.. py:class:: MassValue

   Bases: :py:obj:`msgspec.Struct`


   Single mass field with unit.


   .. py:attribute:: unit
      :type:  bluetooth_sig.types.units.WeightUnit


   .. py:attribute:: value
      :type:  float


.. py:class:: OtherMeasurements

   Bases: :py:obj:`msgspec.Struct`


   Impedance, weight, and height measurements.


   .. py:attribute:: height
      :type:  float | None


   .. py:attribute:: impedance
      :type:  float | None


   .. py:attribute:: weight
      :type:  float | None


.. py:data:: BODY_FAT_PERCENTAGE_RESOLUTION
   :value: 0.1


.. py:data:: HEIGHT_RESOLUTION_IMPERIAL
   :value: 0.1


.. py:data:: HEIGHT_RESOLUTION_METRIC
   :value: 0.001


.. py:data:: IMPEDANCE_RESOLUTION
   :value: 0.1


.. py:data:: MASS_RESOLUTION_KG
   :value: 0.005


.. py:data:: MASS_RESOLUTION_LB
   :value: 0.01


.. py:data:: MUSCLE_PERCENTAGE_RESOLUTION
   :value: 0.1


