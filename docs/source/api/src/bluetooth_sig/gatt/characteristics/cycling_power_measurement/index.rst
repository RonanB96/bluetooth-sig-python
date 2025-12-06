src.bluetooth_sig.gatt.characteristics.cycling_power_measurement
================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.cycling_power_measurement

.. autoapi-nested-parse::

   Cycling Power Measurement characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.cycling_power_measurement.CyclingPowerMeasurementCharacteristic
   src.bluetooth_sig.gatt.characteristics.cycling_power_measurement.CyclingPowerMeasurementData
   src.bluetooth_sig.gatt.characteristics.cycling_power_measurement.CyclingPowerMeasurementFlags


Module Contents
---------------

.. py:class:: CyclingPowerMeasurementCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Cycling Power Measurement characteristic (0x2A63).

   Used to transmit cycling power measurement data including
   instantaneous power, pedal power balance, accumulated energy, and
   revolution data.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> CyclingPowerMeasurementData

      Parse cycling power measurement data according to Bluetooth specification.

      Format: Flags(2) + Instantaneous Power(2) + [Pedal Power Balance(1)] +
      [Accumulated Energy(2)] + [Wheel Revolutions(4)] + [Last Wheel Event Time(2)] +
      [Crank Revolutions(2)] + [Last Crank Event Time(2)]

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: CyclingPowerMeasurementData containing parsed power measurement data.

      :raises ValueError: If data format is invalid.



   .. py:method:: encode_value(data: CyclingPowerMeasurementData) -> bytearray

      Encode cycling power measurement value back to bytes.

      :param data: CyclingPowerMeasurementData containing cycling power measurement data

      :returns: Encoded bytes representing the power measurement



   .. py:attribute:: CRANK_TIME_RESOLUTION
      :value: 1024.0



   .. py:attribute:: PEDAL_POWER_BALANCE_RESOLUTION
      :value: 2.0



   .. py:attribute:: UNKNOWN_PEDAL_POWER_BALANCE
      :value: 255



   .. py:attribute:: WHEEL_TIME_RESOLUTION
      :value: 2048.0



.. py:class:: CyclingPowerMeasurementData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Cycling Power Measurement characteristic.


   .. py:attribute:: accumulated_energy
      :type:  int | None
      :value: None



   .. py:attribute:: cumulative_crank_revolutions
      :type:  int | None
      :value: None



   .. py:attribute:: cumulative_wheel_revolutions
      :type:  int | None
      :value: None



   .. py:attribute:: flags
      :type:  CyclingPowerMeasurementFlags


   .. py:attribute:: instantaneous_power
      :type:  int


   .. py:attribute:: last_crank_event_time
      :type:  float | None
      :value: None



   .. py:attribute:: last_wheel_event_time
      :type:  float | None
      :value: None



   .. py:attribute:: pedal_power_balance
      :type:  float | None
      :value: None



.. py:class:: CyclingPowerMeasurementFlags

   Bases: :py:obj:`enum.IntFlag`


   Cycling Power Measurement Flags as per Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: ACCUMULATED_ENERGY_PRESENT
      :value: 8



   .. py:attribute:: ACCUMULATED_ENERGY_RESERVED
      :value: 2048



   .. py:attribute:: ACCUMULATED_TORQUE_PRESENT
      :value: 4



   .. py:attribute:: BOTTOM_DEAD_SPOT_ANGLE_PRESENT
      :value: 1024



   .. py:attribute:: CRANK_REVOLUTION_DATA_PRESENT
      :value: 32



   .. py:attribute:: EXTREME_ANGLES_PRESENT
      :value: 256



   .. py:attribute:: EXTREME_FORCE_MAGNITUDES_PRESENT
      :value: 64



   .. py:attribute:: EXTREME_TORQUE_MAGNITUDES_PRESENT
      :value: 128



   .. py:attribute:: PEDAL_POWER_BALANCE_PRESENT
      :value: 1



   .. py:attribute:: PEDAL_POWER_BALANCE_REFERENCE
      :value: 2



   .. py:attribute:: TOP_DEAD_SPOT_ANGLE_PRESENT
      :value: 512



   .. py:attribute:: WHEEL_REVOLUTION_DATA_PRESENT
      :value: 16



