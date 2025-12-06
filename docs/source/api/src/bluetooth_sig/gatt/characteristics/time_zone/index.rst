src.bluetooth_sig.gatt.characteristics.time_zone
================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.time_zone

.. autoapi-nested-parse::

   Time Zone characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.time_zone.TimeZoneCharacteristic


Module Contents
---------------

.. py:class:: TimeZoneCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Time Zone characteristic (0x2A0E).

   org.bluetooth.characteristic.time_zone

   Time zone characteristic.

   Represents the time difference in 15-minute increments between local
   standard time and UTC.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> str

      Parse time zone data (sint8 in 15-minute increments from UTC).



   .. py:method:: encode_value(data: str | int) -> bytearray

      Encode time zone value back to bytes.

      :param data: Time zone offset either as string (e.g., "UTC+05:30") or as raw sint8 value

      :returns: Encoded bytes representing the time zone (sint8, 15-minute increments)



