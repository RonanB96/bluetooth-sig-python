src.bluetooth_sig.gatt.characteristics.position_quality
=======================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.position_quality

.. autoapi-nested-parse::

   Position Quality characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.position_quality.PositionQualityCharacteristic
   src.bluetooth_sig.gatt.characteristics.position_quality.PositionQualityData
   src.bluetooth_sig.gatt.characteristics.position_quality.PositionQualityFlags


Module Contents
---------------

.. py:class:: PositionQualityCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Position Quality characteristic.

   Used to represent data related to the quality of a position measurement.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> PositionQualityData

      Parse position quality data according to Bluetooth specification.

      Format: Flags(2) + [Number of Beacons in Solution(1)] + [Number of Beacons in View(1)] +
      [Time to First Fix(2)] + [EHPE(4)] + [EVPE(4)] + [HDOP(1)] + [VDOP(1)].

      :param data: Raw bytearray from BLE characteristic
      :param ctx: Optional context providing surrounding context (may be None)

      :returns: PositionQualityData containing parsed position quality data



   .. py:method:: encode_value(data: PositionQualityData) -> bytearray

      Encode PositionQualityData back to bytes.

      :param data: PositionQualityData instance to encode

      :returns: Encoded bytes representing the position quality data



   .. py:attribute:: POSITION_STATUS_MASK
      :value: 384



   .. py:attribute:: POSITION_STATUS_SHIFT
      :value: 7



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: True



   .. py:attribute:: max_length
      :value: 16



   .. py:attribute:: min_length
      :value: 2



.. py:class:: PositionQualityData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Position Quality characteristic.


   .. py:attribute:: ehpe
      :type:  float | None
      :value: None



   .. py:attribute:: evpe
      :type:  float | None
      :value: None



   .. py:attribute:: flags
      :type:  PositionQualityFlags


   .. py:attribute:: hdop
      :type:  float | None
      :value: None



   .. py:attribute:: number_of_beacons_in_solution
      :type:  int | None
      :value: None



   .. py:attribute:: number_of_beacons_in_view
      :type:  int | None
      :value: None



   .. py:attribute:: position_status
      :type:  src.bluetooth_sig.types.location.PositionStatus | None
      :value: None



   .. py:attribute:: time_to_first_fix
      :type:  float | None
      :value: None



   .. py:attribute:: vdop
      :type:  float | None
      :value: None



.. py:class:: PositionQualityFlags

   Bases: :py:obj:`enum.IntFlag`


   Position Quality flags as per Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: EHPE_PRESENT
      :value: 8



   .. py:attribute:: EVPE_PRESENT
      :value: 16



   .. py:attribute:: HDOP_PRESENT
      :value: 32



   .. py:attribute:: NUMBER_OF_BEACONS_IN_SOLUTION_PRESENT
      :value: 1



   .. py:attribute:: NUMBER_OF_BEACONS_IN_VIEW_PRESENT
      :value: 2



   .. py:attribute:: TIME_TO_FIRST_FIX_PRESENT
      :value: 4



   .. py:attribute:: VDOP_PRESENT
      :value: 64



