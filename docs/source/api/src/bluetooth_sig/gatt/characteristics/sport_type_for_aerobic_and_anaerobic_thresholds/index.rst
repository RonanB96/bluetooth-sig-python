src.bluetooth_sig.gatt.characteristics.sport_type_for_aerobic_and_anaerobic_thresholds
======================================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.sport_type_for_aerobic_and_anaerobic_thresholds

.. autoapi-nested-parse::

   Sport Type for Aerobic and Anaerobic Thresholds characteristic (0x2A93).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.sport_type_for_aerobic_and_anaerobic_thresholds.SportType
   src.bluetooth_sig.gatt.characteristics.sport_type_for_aerobic_and_anaerobic_thresholds.SportTypeForAerobicAndAnaerobicThresholdsCharacteristic


Module Contents
---------------

.. py:class:: SportType

   Bases: :py:obj:`enum.IntEnum`


   Sport type enumeration for aerobic and anaerobic thresholds.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: ARM_EXERCISING
      :value: 8



   .. py:attribute:: CLIMBING
      :value: 5



   .. py:attribute:: CROSS_TRAINING_ELLIPTICAL
      :value: 4



   .. py:attribute:: CYCLING_ERGOMETER
      :value: 2



   .. py:attribute:: LOWER_BODY_EXERCISING
      :value: 9



   .. py:attribute:: ROWING_ERGOMETER
      :value: 3



   .. py:attribute:: RUNNING_TREADMILL
      :value: 1



   .. py:attribute:: SKATING
      :value: 7



   .. py:attribute:: SKIING
      :value: 6



   .. py:attribute:: UNSPECIFIED
      :value: 0



   .. py:attribute:: UPPER_BODY_EXERCISING
      :value: 10



   .. py:attribute:: WHOLE_BODY_EXERCISING
      :value: 11



.. py:class:: SportTypeForAerobicAndAnaerobicThresholdsCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Sport Type for Aerobic and Anaerobic Thresholds characteristic (0x2A93).

   org.bluetooth.characteristic.sport_type_for_aerobic_and_anaerobic_thresholds

   The Sport Type for Aerobic and Anaerobic Thresholds characteristic is used to represent
   the sport type applicable to aerobic and anaerobic thresholds for a user.


   .. py:method:: decode_value(data: bytearray, ctx: bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> SportType

      Decode sport type from raw bytes.

      :param data: Raw bytes from BLE characteristic (1 byte)
      :param ctx: Optional context for parsing

      :returns: SportType enum value

      :raises ValueError: If data length is not exactly 1 byte or value is invalid



   .. py:method:: encode_value(data: SportType) -> bytearray

      Encode sport type to raw bytes.

      :param data: SportType enum value

      :returns: Encoded bytes
      :rtype: bytearray



   .. py:attribute:: expected_length
      :value: 1



