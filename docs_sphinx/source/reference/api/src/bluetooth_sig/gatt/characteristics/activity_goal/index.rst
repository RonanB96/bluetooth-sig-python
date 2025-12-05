src.bluetooth_sig.gatt.characteristics.activity_goal
====================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.activity_goal

.. autoapi-nested-parse::

   Activity Goal characteristic (0x2B4E).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.activity_goal.ActivityGoalPresenceFlags
   src.bluetooth_sig.gatt.characteristics.activity_goal.ActivityGoalData
   src.bluetooth_sig.gatt.characteristics.activity_goal.ActivityGoalCharacteristic


Module Contents
---------------

.. py:class:: ActivityGoalPresenceFlags

   Bases: :py:obj:`enum.IntFlag`


   Presence flags for Activity Goal characteristic.


   .. py:attribute:: TOTAL_ENERGY_EXPENDITURE
      :value: 1



   .. py:attribute:: NORMAL_WALKING_STEPS
      :value: 2



   .. py:attribute:: INTENSITY_STEPS
      :value: 4



   .. py:attribute:: FLOOR_STEPS
      :value: 8



   .. py:attribute:: DISTANCE
      :value: 16



   .. py:attribute:: DURATION_NORMAL_WALKING
      :value: 32



   .. py:attribute:: DURATION_INTENSITY_WALKING
      :value: 64



.. py:class:: ActivityGoalData

   Bases: :py:obj:`msgspec.Struct`


   Activity Goal data structure.


   .. py:attribute:: presence_flags
      :type:  ActivityGoalPresenceFlags


   .. py:attribute:: total_energy_expenditure
      :type:  int | None
      :value: None



   .. py:attribute:: normal_walking_steps
      :type:  int | None
      :value: None



   .. py:attribute:: intensity_steps
      :type:  int | None
      :value: None



   .. py:attribute:: floor_steps
      :type:  int | None
      :value: None



   .. py:attribute:: distance
      :type:  int | None
      :value: None



   .. py:attribute:: duration_normal_walking
      :type:  int | None
      :value: None



   .. py:attribute:: duration_intensity_walking
      :type:  int | None
      :value: None



.. py:class:: ActivityGoalCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Activity Goal characteristic (0x2B4E).

   org.bluetooth.characteristic.activity_goal

   The Activity Goal characteristic is used to represent the goal or target of a user,
   such as number of steps or total energy expenditure, related to a physical activity session.


   .. py:attribute:: min_length
      :type:  int
      :value: 1



   .. py:attribute:: max_length
      :type:  int
      :value: 22



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> ActivityGoalData

      Decode Activity Goal from raw bytes.

      :param data: Raw bytes from BLE characteristic
      :param ctx: Optional context for parsing

      :returns: Parsed activity goal
      :rtype: ActivityGoalData

      :raises InsufficientDataError: If data is insufficient for parsing



   .. py:method:: encode_value(data: ActivityGoalData) -> bytearray

      Encode Activity Goal to raw bytes.

      :param data: ActivityGoalData to encode

      :returns: Encoded bytes
      :rtype: bytearray



