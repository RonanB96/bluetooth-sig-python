src.bluetooth_sig.gatt.characteristics.blood_pressure_common
============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.blood_pressure_common

.. autoapi-nested-parse::

   Shared constants and types for blood pressure characteristics.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BLOOD_PRESSURE_MAX_MMHG
   src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BLOOD_PRESSURE_MAX_KPA


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BloodPressureFlags
   src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BloodPressureOptionalFields
   src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BloodPressureDataProtocol
   src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BaseBloodPressureCharacteristic


Module Contents
---------------

.. py:data:: BLOOD_PRESSURE_MAX_MMHG
   :value: 300


.. py:data:: BLOOD_PRESSURE_MAX_KPA
   :value: 40


.. py:class:: BloodPressureFlags

   Bases: :py:obj:`enum.IntFlag`


   Blood Pressure flags as per Bluetooth SIG specification.


   .. py:attribute:: UNITS_KPA
      :value: 1



   .. py:attribute:: TIMESTAMP_PRESENT
      :value: 2



   .. py:attribute:: PULSE_RATE_PRESENT
      :value: 4



   .. py:attribute:: USER_ID_PRESENT
      :value: 8



   .. py:attribute:: MEASUREMENT_STATUS_PRESENT
      :value: 16



.. py:class:: BloodPressureOptionalFields

   Bases: :py:obj:`msgspec.Struct`


   Optional fields common to blood pressure characteristics.


   .. py:attribute:: timestamp
      :type:  datetime.datetime | None
      :value: None



   .. py:attribute:: pulse_rate
      :type:  float | None
      :value: None



   .. py:attribute:: user_id
      :type:  int | None
      :value: None



   .. py:attribute:: measurement_status
      :type:  int | None
      :value: None



.. py:class:: BloodPressureDataProtocol

   Bases: :py:obj:`Protocol`


   Protocol for blood pressure data structs with unit field.


   .. py:property:: unit
      :type: bluetooth_sig.types.units.PressureUnit


      Pressure unit for blood pressure measurement.


.. py:class:: BaseBloodPressureCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Base class for blood pressure characteristics with common parsing logic.


   .. py:attribute:: min_length
      :value: 7



   .. py:attribute:: max_length
      :value: 19



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: True



