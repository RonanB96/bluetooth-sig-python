src.bluetooth_sig.gatt.characteristics.blood_pressure_common
============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.blood_pressure_common

.. autoapi-nested-parse::

   Shared constants and types for blood pressure characteristics.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BLOOD_PRESSURE_MAX_KPA
   src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BLOOD_PRESSURE_MAX_MMHG


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BaseBloodPressureCharacteristic
   src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BloodPressureDataProtocol
   src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BloodPressureFlags
   src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BloodPressureOptionalFields


Module Contents
---------------

.. py:class:: BaseBloodPressureCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Base class for blood pressure characteristics with common parsing logic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: True



   .. py:attribute:: max_length
      :value: 19



   .. py:attribute:: min_length
      :value: 7



.. py:class:: BloodPressureDataProtocol

   Bases: :py:obj:`Protocol`


   Protocol for blood pressure data structs with unit field.


   .. py:property:: unit
      :type: bluetooth_sig.types.units.PressureUnit


      Pressure unit for blood pressure measurement.


.. py:class:: BloodPressureFlags

   Bases: :py:obj:`enum.IntFlag`


   Blood Pressure flags as per Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: MEASUREMENT_STATUS_PRESENT
      :value: 16



   .. py:attribute:: PULSE_RATE_PRESENT
      :value: 4



   .. py:attribute:: TIMESTAMP_PRESENT
      :value: 2



   .. py:attribute:: UNITS_KPA
      :value: 1



   .. py:attribute:: USER_ID_PRESENT
      :value: 8



.. py:class:: BloodPressureOptionalFields

   Bases: :py:obj:`msgspec.Struct`


   Optional fields common to blood pressure characteristics.


   .. py:attribute:: measurement_status
      :type:  int | None
      :value: None



   .. py:attribute:: pulse_rate
      :type:  float | None
      :value: None



   .. py:attribute:: timestamp
      :type:  datetime.datetime | None
      :value: None



   .. py:attribute:: user_id
      :type:  int | None
      :value: None



.. py:data:: BLOOD_PRESSURE_MAX_KPA
   :value: 40


.. py:data:: BLOOD_PRESSURE_MAX_MMHG
   :value: 300


