src.bluetooth_sig.gatt.characteristics.location_and_speed
=========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.location_and_speed

.. autoapi-nested-parse::

   Location and Speed characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.location_and_speed.ElevationSource
   src.bluetooth_sig.gatt.characteristics.location_and_speed.HeadingSource
   src.bluetooth_sig.gatt.characteristics.location_and_speed.LocationAndSpeedCharacteristic
   src.bluetooth_sig.gatt.characteristics.location_and_speed.LocationAndSpeedData
   src.bluetooth_sig.gatt.characteristics.location_and_speed.LocationAndSpeedFlags
   src.bluetooth_sig.gatt.characteristics.location_and_speed.SpeedAndDistanceFormat


Module Contents
---------------

.. py:class:: ElevationSource

   Bases: :py:obj:`enum.IntEnum`


   Elevation source enumeration.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: BAROMETRIC_AIR_PRESSURE
      :value: 1



   .. py:attribute:: DATABASE_SERVICE
      :value: 2



   .. py:attribute:: OTHER
      :value: 3



   .. py:attribute:: POSITIONING_SYSTEM
      :value: 0



.. py:class:: HeadingSource

   Bases: :py:obj:`enum.IntEnum`


   Heading source enumeration.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: HEADING_BASED_ON_MAGNETIC_COMPASS
      :value: 1



   .. py:attribute:: HEADING_BASED_ON_MOVEMENT
      :value: 0



.. py:class:: LocationAndSpeedCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Location and Speed characteristic.

   Used to represent data related to a location and speed sensor.
   Note that it is possible for this characteristic to exceed the default LE ATT_MTU size.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> LocationAndSpeedData

      Parse location and speed data according to Bluetooth specification.

      Format: Flags(2) + [Instantaneous Speed(2)] + [Total Distance(3)] + [Location - Latitude(4)] +
      [Location - Longitude(4)] + [Elevation(3)] + [Heading(2)] + [Rolling Time(1)] + [UTC Time(7)].

      :param data: Raw bytearray from BLE characteristic
      :param ctx: Optional context providing surrounding context (may be None)

      :returns: LocationAndSpeedData containing parsed location and speed data



   .. py:method:: encode_value(data: LocationAndSpeedData) -> bytearray

      Encode LocationAndSpeedData back to bytes.

      :param data: LocationAndSpeedData instance to encode

      :returns: Encoded bytes representing the location and speed data



   .. py:attribute:: ELEVATION_SOURCE_MASK
      :value: 6144



   .. py:attribute:: ELEVATION_SOURCE_SHIFT
      :value: 11



   .. py:attribute:: HEADING_SOURCE_MASK
      :value: 8192



   .. py:attribute:: HEADING_SOURCE_SHIFT
      :value: 13



   .. py:attribute:: POSITION_STATUS_MASK
      :value: 768



   .. py:attribute:: POSITION_STATUS_SHIFT
      :value: 8



   .. py:attribute:: SPEED_DISTANCE_FORMAT_MASK
      :value: 1024



   .. py:attribute:: SPEED_DISTANCE_FORMAT_SHIFT
      :value: 10



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: True



   .. py:attribute:: max_length
      :value: 28



   .. py:attribute:: min_length
      :value: 2



.. py:class:: LocationAndSpeedData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Location and Speed characteristic.


   .. py:attribute:: elevation
      :type:  float | None
      :value: None



   .. py:attribute:: elevation_source
      :type:  ElevationSource | None
      :value: None



   .. py:attribute:: flags
      :type:  LocationAndSpeedFlags


   .. py:attribute:: heading
      :type:  float | None
      :value: None



   .. py:attribute:: heading_source
      :type:  HeadingSource | None
      :value: None



   .. py:attribute:: instantaneous_speed
      :type:  float | None
      :value: None



   .. py:attribute:: latitude
      :type:  float | None
      :value: None



   .. py:attribute:: longitude
      :type:  float | None
      :value: None



   .. py:attribute:: position_status
      :type:  src.bluetooth_sig.types.location.PositionStatus | None
      :value: None



   .. py:attribute:: rolling_time
      :type:  int | None
      :value: None



   .. py:attribute:: speed_and_distance_format
      :type:  SpeedAndDistanceFormat | None
      :value: None



   .. py:attribute:: total_distance
      :type:  float | None
      :value: None



   .. py:attribute:: utc_time
      :type:  datetime.datetime | None
      :value: None



.. py:class:: LocationAndSpeedFlags

   Bases: :py:obj:`enum.IntFlag`


   Location and Speed flags as per Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: ELEVATION_PRESENT
      :value: 8



   .. py:attribute:: HEADING_PRESENT
      :value: 16



   .. py:attribute:: INSTANTANEOUS_SPEED_PRESENT
      :value: 1



   .. py:attribute:: LOCATION_PRESENT
      :value: 4



   .. py:attribute:: ROLLING_TIME_PRESENT
      :value: 32



   .. py:attribute:: TOTAL_DISTANCE_PRESENT
      :value: 2



   .. py:attribute:: UTC_TIME_PRESENT
      :value: 64



.. py:class:: SpeedAndDistanceFormat

   Bases: :py:obj:`enum.IntEnum`


   Speed and distance format enumeration.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: FORMAT_2D
      :value: 0



   .. py:attribute:: FORMAT_3D
      :value: 1



