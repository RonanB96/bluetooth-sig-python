src.bluetooth_sig.gatt.characteristics.five_zone_heart_rate_limits
==================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.five_zone_heart_rate_limits

.. autoapi-nested-parse::

   Five Zone Heart Rate Limits characteristic (0x2A8B).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.five_zone_heart_rate_limits.FiveZoneHeartRateLimitsData
   src.bluetooth_sig.gatt.characteristics.five_zone_heart_rate_limits.FiveZoneHeartRateLimitsCharacteristic


Module Contents
---------------

.. py:class:: FiveZoneHeartRateLimitsData

   Bases: :py:obj:`msgspec.Struct`


   Five Zone Heart Rate Limits data structure.


   .. py:attribute:: very_light_light_limit
      :type:  int


   .. py:attribute:: light_moderate_limit
      :type:  int


   .. py:attribute:: moderate_hard_limit
      :type:  int


   .. py:attribute:: hard_maximum_limit
      :type:  int


.. py:class:: FiveZoneHeartRateLimitsCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Five Zone Heart Rate Limits characteristic (0x2A8B).

   org.bluetooth.characteristic.five_zone_heart_rate_limits

   The Five Zone Heart Rate Limits characteristic is used to represent the limits
   between the heart rate zones for the five-zone heart rate definition
   (Maximum, Hard, Moderate, Light, and Very Light) of a user.


   .. py:attribute:: expected_length
      :value: 4



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> FiveZoneHeartRateLimitsData

      Decode Five Zone Heart Rate Limits from raw bytes.

      :param data: Raw bytes from BLE characteristic (4 bytes)
      :param ctx: Optional context for parsing

      :returns: Parsed heart rate limits
      :rtype: FiveZoneHeartRateLimitsData



   .. py:method:: encode_value(data: FiveZoneHeartRateLimitsData) -> bytearray

      Encode Five Zone Heart Rate Limits to raw bytes.

      :param data: FiveZoneHeartRateLimitsData to encode

      :returns: Encoded bytes
      :rtype: bytearray



