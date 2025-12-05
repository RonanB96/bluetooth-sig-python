src.bluetooth_sig.gatt.characteristics.noise
============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.noise

.. autoapi-nested-parse::

   Noise (Sound Pressure Level) characteristic implementation.

   Per Bluetooth SIG specification (UUID 0x2BE4):
   - Data type: uint8 (1 byte)
   - Unit: decibel SPL with 1 dB resolution
   - Range: 0-253 dB
   - Special values: 0xFE (≥254 dB), 0xFF (unknown)



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.noise.NoiseCharacteristic


Module Contents
---------------

.. py:class:: NoiseCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Noise characteristic (0x2BE4) - Sound pressure level measurement.

   Represents sound pressure level in decibels (dB SPL) per SIG specification.
   Uses uint8 format with 1 dB resolution.

   Valid range: 0-253 dB
   Special values:
   - 0xFE (254): Value is 254 dB or greater
   - 0xFF (255): Value is not known


   .. py:attribute:: UNKNOWN_VALUE
      :value: 255



   .. py:attribute:: MAX_OR_GREATER_VALUE
      :value: 254



   .. py:attribute:: MAX_MEASURABLE_VALUE
      :value: 254



   .. py:attribute:: MAX_NORMAL_VALUE
      :value: 253



   .. py:attribute:: min_value
      :type:  int | float | None
      :value: 0



   .. py:attribute:: max_value
      :type:  int | float | None
      :value: 254



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> int | None

      Decode noise level with special value handling.



   .. py:method:: encode_value(data: int | None) -> bytearray

      Encode noise level with special value handling.



