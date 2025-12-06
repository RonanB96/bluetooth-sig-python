src.bluetooth_sig.gatt.characteristics.cycling_power_vector
===========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.cycling_power_vector

.. autoapi-nested-parse::

   Cycling Power Vector characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.cycling_power_vector.CrankRevolutionData
   src.bluetooth_sig.gatt.characteristics.cycling_power_vector.CyclingPowerVectorCharacteristic
   src.bluetooth_sig.gatt.characteristics.cycling_power_vector.CyclingPowerVectorData
   src.bluetooth_sig.gatt.characteristics.cycling_power_vector.CyclingPowerVectorFlags


Module Contents
---------------

.. py:class:: CrankRevolutionData

   Bases: :py:obj:`msgspec.Struct`


   Crank revolution data from cycling power vector.


   .. py:attribute:: crank_revolutions
      :type:  int


   .. py:attribute:: last_crank_event_time
      :type:  float


.. py:class:: CyclingPowerVectorCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Cycling Power Vector characteristic (0x2A64).

   Used to transmit detailed cycling power vector data including force
   and torque measurements at different crank angles.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> CyclingPowerVectorData

      Parse cycling power vector data according to Bluetooth specification.

      Format: Flags(1) + Crank Revolution Data(2) + Last Crank Event Time(2) +
      First Crank Measurement Angle(2) + [Instantaneous Force Magnitude Array] +
      [Instantaneous Torque Magnitude Array]

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: CyclingPowerVectorData containing parsed cycling power vector data.

      # `ctx` is intentionally unused in this implementation; mark as used
      # so linters do not report an unused-argument error.
      del ctx
      :raises ValueError: If data format is invalid.



   .. py:method:: encode_value(data: CyclingPowerVectorData) -> bytearray

      Encode cycling power vector value back to bytes.

      :param data: CyclingPowerVectorData containing cycling power vector data

      :returns: Encoded bytes representing the power vector



.. py:class:: CyclingPowerVectorData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Cycling Power Vector characteristic.

   Used for both parsing and encoding - all fields are properly typed.


   .. py:attribute:: crank_revolution_data
      :type:  CrankRevolutionData


   .. py:attribute:: first_crank_measurement_angle
      :type:  float


   .. py:attribute:: flags
      :type:  CyclingPowerVectorFlags


   .. py:attribute:: instantaneous_force_magnitude_array
      :type:  tuple[float, Ellipsis] | None
      :value: None



   .. py:attribute:: instantaneous_torque_magnitude_array
      :type:  tuple[float, Ellipsis] | None
      :value: None



.. py:class:: CyclingPowerVectorFlags

   Bases: :py:obj:`enum.IntFlag`


   Cycling Power Vector flags as per Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: INSTANTANEOUS_FORCE_MAGNITUDE_ARRAY_PRESENT
      :value: 1



   .. py:attribute:: INSTANTANEOUS_TORQUE_MAGNITUDE_ARRAY_PRESENT
      :value: 2



