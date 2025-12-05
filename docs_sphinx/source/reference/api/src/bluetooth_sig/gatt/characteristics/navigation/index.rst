src.bluetooth_sig.gatt.characteristics.navigation
=================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.navigation

.. autoapi-nested-parse::

   Navigation characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.navigation.NavigationFlags
   src.bluetooth_sig.gatt.characteristics.navigation.NavigationIndicatorType
   src.bluetooth_sig.gatt.characteristics.navigation.NavigationData
   src.bluetooth_sig.gatt.characteristics.navigation.HeadingSource
   src.bluetooth_sig.gatt.characteristics.navigation.NavigationCharacteristic


Module Contents
---------------

.. py:class:: NavigationFlags

   Bases: :py:obj:`enum.IntFlag`


   Navigation flags as per Bluetooth SIG specification.


   .. py:attribute:: REMAINING_DISTANCE_PRESENT
      :value: 1



   .. py:attribute:: REMAINING_VERTICAL_DISTANCE_PRESENT
      :value: 2



   .. py:attribute:: ESTIMATED_TIME_OF_ARRIVAL_PRESENT
      :value: 4



.. py:class:: NavigationIndicatorType

   Bases: :py:obj:`enum.IntEnum`


   Navigation indicator type enumeration.


   .. py:attribute:: TO_WAYPOINT
      :value: 0



   .. py:attribute:: TO_DESTINATION
      :value: 1



.. py:class:: NavigationData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Navigation characteristic.


   .. py:attribute:: flags
      :type:  NavigationFlags


   .. py:attribute:: bearing
      :type:  float


   .. py:attribute:: heading
      :type:  float


   .. py:attribute:: remaining_distance
      :type:  float | None
      :value: None



   .. py:attribute:: remaining_vertical_distance
      :type:  float | None
      :value: None



   .. py:attribute:: estimated_time_of_arrival
      :type:  datetime.datetime | None
      :value: None



   .. py:attribute:: position_status
      :type:  src.bluetooth_sig.types.location.PositionStatus | None
      :value: None



   .. py:attribute:: heading_source
      :type:  HeadingSource | None
      :value: None



   .. py:attribute:: navigation_indicator_type
      :type:  NavigationIndicatorType | None
      :value: None



   .. py:attribute:: waypoint_reached
      :type:  bool | None
      :value: None



   .. py:attribute:: destination_reached
      :type:  bool | None
      :value: None



.. py:class:: HeadingSource

   Bases: :py:obj:`enum.IntEnum`


   Heading source enumeration.


   .. py:attribute:: HEADING_BASED_ON_MOVEMENT
      :value: 0



   .. py:attribute:: HEADING_BASED_ON_MAGNETIC_COMPASS
      :value: 1



.. py:class:: NavigationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Navigation characteristic.

   Used to represent data related to a navigation sensor.


   .. py:attribute:: min_length
      :value: 6



   .. py:attribute:: max_length
      :value: 16



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: True



   .. py:attribute:: POSITION_STATUS_MASK
      :value: 6



   .. py:attribute:: POSITION_STATUS_SHIFT
      :value: 1



   .. py:attribute:: HEADING_SOURCE_MASK
      :value: 32



   .. py:attribute:: HEADING_SOURCE_SHIFT
      :value: 5



   .. py:attribute:: NAVIGATION_INDICATOR_TYPE_MASK
      :value: 64



   .. py:attribute:: NAVIGATION_INDICATOR_TYPE_SHIFT
      :value: 6



   .. py:attribute:: WAYPOINT_REACHED_MASK
      :value: 128



   .. py:attribute:: DESTINATION_REACHED_MASK
      :value: 256



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> NavigationData

      Parse navigation data according to Bluetooth specification.

      Format: Flags(2) + Bearing(2) + Heading(2) + [Remaining Distance(3)] +
      [Remaining Vertical Distance(3)] + [Estimated Time of Arrival(7)].

      :param data: Raw bytearray from BLE characteristic
      :param ctx: Optional context providing surrounding context (may be None)

      :returns: NavigationData containing parsed navigation data



   .. py:method:: encode_value(data: NavigationData) -> bytearray

      Encode NavigationData back to bytes.

      :param data: NavigationData instance to encode

      :returns: Encoded bytes representing the navigation data



