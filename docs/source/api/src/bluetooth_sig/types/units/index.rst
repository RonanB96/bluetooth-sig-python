src.bluetooth_sig.types.units
=============================

.. py:module:: src.bluetooth_sig.types.units

.. autoapi-nested-parse::

   Unit enumerations for measurements and data types.

   Defines enums for measurement systems, weight units, height units,
   temperature units, and other unit types to replace string usage with type-safe alternatives.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.units.AngleUnit
   src.bluetooth_sig.types.units.ConcentrationUnit
   src.bluetooth_sig.types.units.ElectricalUnit
   src.bluetooth_sig.types.units.GlucoseConcentrationUnit
   src.bluetooth_sig.types.units.HeightUnit
   src.bluetooth_sig.types.units.LengthUnit
   src.bluetooth_sig.types.units.MeasurementSystem
   src.bluetooth_sig.types.units.PercentageUnit
   src.bluetooth_sig.types.units.PhysicalUnit
   src.bluetooth_sig.types.units.PressureUnit
   src.bluetooth_sig.types.units.SoundUnit
   src.bluetooth_sig.types.units.TemperatureUnit
   src.bluetooth_sig.types.units.WeightUnit


Module Contents
---------------

.. py:class:: AngleUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for angle measurements.


   .. py:attribute:: DEGREES
      :value: '°'



.. py:class:: ConcentrationUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for concentration measurements.


   .. py:attribute:: GRAINS_PER_CUBIC_METER
      :value: 'grains/m³'



   .. py:attribute:: KILOGRAMS_PER_CUBIC_METER
      :value: 'kg/m³'



   .. py:attribute:: MICROGRAMS_PER_CUBIC_METER
      :value: 'µg/m³'



   .. py:attribute:: PARTS_PER_BILLION
      :value: 'ppb'



   .. py:attribute:: PARTS_PER_MILLION
      :value: 'ppm'



.. py:class:: ElectricalUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for electrical measurements.


   .. py:attribute:: AMPS
      :value: 'A'



   .. py:attribute:: DBM
      :value: 'dBm'



   .. py:attribute:: HERTZ
      :value: 'Hz'



   .. py:attribute:: VOLTS
      :value: 'V'



.. py:class:: GlucoseConcentrationUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for glucose concentration measurements.


   .. py:attribute:: MG_DL
      :value: 'mg/dL'



   .. py:attribute:: MMOL_L
      :value: 'mmol/L'



.. py:class:: HeightUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for height measurements.


   .. py:attribute:: INCHES
      :value: 'inches'



   .. py:attribute:: METERS
      :value: 'meters'



.. py:class:: LengthUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for length measurements.


   .. py:attribute:: INCHES
      :value: "'"



   .. py:attribute:: METERS
      :value: 'm'



   .. py:attribute:: MILLIMETERS
      :value: 'mm'



.. py:class:: MeasurementSystem(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Measurement system for body composition and weight data.


   .. py:attribute:: IMPERIAL
      :value: 'imperial'



   .. py:attribute:: METRIC
      :value: 'metric'



.. py:class:: PercentageUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for percentage measurements.


   .. py:attribute:: PERCENT
      :value: '%'



.. py:class:: PhysicalUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for physical measurements.


   .. py:attribute:: TESLA
      :value: 'T'



.. py:class:: PressureUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for pressure measurements.


   .. py:attribute:: KPA
      :value: 'kPa'



   .. py:attribute:: MMHG
      :value: 'mmHg'



.. py:class:: SoundUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for sound measurements.


   .. py:attribute:: DECIBELS_SPL
      :value: 'dB SPL'



.. py:class:: TemperatureUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for temperature measurements.


   .. py:attribute:: CELSIUS
      :value: '°C'



   .. py:attribute:: FAHRENHEIT
      :value: '°F'



.. py:class:: WeightUnit(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Units for weight/mass measurements.


   .. py:attribute:: KG
      :value: 'kg'



   .. py:attribute:: LB
      :value: 'lb'



