src.bluetooth_sig.gatt.characteristics.intermediate_cuff_pressure
=================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.intermediate_cuff_pressure

.. autoapi-nested-parse::

   Intermediate Cuff Pressure characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.intermediate_cuff_pressure.IntermediateCuffPressureCharacteristic
   src.bluetooth_sig.gatt.characteristics.intermediate_cuff_pressure.IntermediateCuffPressureData


Module Contents
---------------

.. py:class:: IntermediateCuffPressureCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BaseBloodPressureCharacteristic`


   Intermediate Cuff Pressure characteristic (0x2A36).

   Used to transmit intermediate cuff pressure values during a blood
   pressure measurement process.

   SIG Specification Pattern:
   This characteristic can use Blood Pressure Feature (0x2A49) to interpret
   which status flags are supported by the device.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> IntermediateCuffPressureData

      Parse intermediate cuff pressure data according to Bluetooth specification.

      Format: Flags(1) + Current Cuff Pressure(2) + Unused(2) + Unused(2) + [Timestamp(7)] +
      [Pulse Rate(2)] + [User ID(1)] + [Measurement Status(2)].
      All pressure values are IEEE-11073 16-bit SFLOAT. Unused fields are set to NaN.

      :param data: Raw bytearray from BLE characteristic
      :param ctx: Optional context providing access to Blood Pressure Feature characteristic
                  for validating which measurement status flags are supported

      :returns: IntermediateCuffPressureData containing parsed cuff pressure data with metadata

      SIG Pattern:
      When context is available, can validate that measurement status flags are
      within the device's supported features as indicated by Blood Pressure Feature.




   .. py:method:: encode_value(data: IntermediateCuffPressureData) -> bytearray

      Encode IntermediateCuffPressureData back to bytes.

      :param data: IntermediateCuffPressureData instance to encode

      :returns: Encoded bytes representing the intermediate cuff pressure



.. py:class:: IntermediateCuffPressureData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Intermediate Cuff Pressure characteristic.


   .. py:attribute:: current_cuff_pressure
      :type:  float


   .. py:attribute:: flags
      :type:  src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BloodPressureFlags


   .. py:attribute:: optional_fields
      :type:  src.bluetooth_sig.gatt.characteristics.blood_pressure_common.BloodPressureOptionalFields


   .. py:attribute:: unit
      :type:  bluetooth_sig.types.units.PressureUnit


