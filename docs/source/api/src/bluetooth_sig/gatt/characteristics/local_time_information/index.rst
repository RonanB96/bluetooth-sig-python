src.bluetooth_sig.gatt.characteristics.local_time_information
=============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.local_time_information

.. autoapi-nested-parse::

   Local Time Information characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.local_time_information.DSTOffset
   src.bluetooth_sig.gatt.characteristics.local_time_information.DSTOffsetInfo
   src.bluetooth_sig.gatt.characteristics.local_time_information.LocalTimeInformationCharacteristic
   src.bluetooth_sig.gatt.characteristics.local_time_information.LocalTimeInformationData
   src.bluetooth_sig.gatt.characteristics.local_time_information.TimezoneInfo


Module Contents
---------------

.. py:class:: DSTOffset

   Bases: :py:obj:`enum.IntEnum`


   DST offset values as an IntEnum to avoid magic numbers.

   Values correspond to the Bluetooth SIG encoded DST offset values.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: DAYLIGHT
      :value: 4



   .. py:attribute:: DOUBLE_DAYLIGHT
      :value: 8



   .. py:attribute:: HALF_HOUR
      :value: 2



   .. py:attribute:: STANDARD
      :value: 0



   .. py:attribute:: UNKNOWN
      :value: 255



   .. py:property:: description
      :type: str


      Human-readable description for this DST offset value.


   .. py:property:: offset_hours
      :type: float | None


      Return the DST offset in hours (e.g. 0.5 for half hour), or None if unknown.


.. py:class:: DSTOffsetInfo

   Bases: :py:obj:`msgspec.Struct`


   DST offset information part of local time data.


   .. py:attribute:: description
      :type:  str


   .. py:attribute:: offset_hours
      :type:  float | None


   .. py:attribute:: raw_value
      :type:  int


.. py:class:: LocalTimeInformationCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Local Time Information characteristic (0x2A0F).

   org.bluetooth.characteristic.local_time_information

   Local time information characteristic.

   Represents the relation (offset) between local time and UTC.
   Contains time zone and Daylight Savings Time (DST) offset
   information.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> LocalTimeInformationData

      Parse local time information data (2 bytes: time zone + DST offset).

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).



   .. py:method:: encode_value(data: LocalTimeInformationData) -> bytearray

      Encode LocalTimeInformationData back to bytes.

      :param data: LocalTimeInformationData instance to encode

      :returns: Encoded bytes representing the local time information



.. py:class:: LocalTimeInformationData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Local Time Information characteristic.


   .. py:attribute:: dst_offset
      :type:  DSTOffsetInfo


   .. py:attribute:: timezone
      :type:  TimezoneInfo


   .. py:attribute:: total_offset_hours
      :type:  float | None
      :value: None



.. py:class:: TimezoneInfo

   Bases: :py:obj:`msgspec.Struct`


   Timezone information part of local time data.


   .. py:attribute:: description
      :type:  str


   .. py:attribute:: offset_hours
      :type:  float | None


   .. py:attribute:: raw_value
      :type:  int


