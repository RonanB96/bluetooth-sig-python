src.bluetooth_sig.gatt.characteristics.four_zone_heart_rate_limits
==================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.four_zone_heart_rate_limits

.. autoapi-nested-parse::

   Four Zone Heart Rate Limits characteristic (0x2B4C).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.four_zone_heart_rate_limits.FourZoneHeartRateLimitsCharacteristic
   src.bluetooth_sig.gatt.characteristics.four_zone_heart_rate_limits.FourZoneHeartRateLimitsData


Module Contents
---------------

.. py:class:: FourZoneHeartRateLimitsCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Four Zone Heart Rate Limits characteristic (0x2B4C).

   org.bluetooth.characteristic.four_zone_heart_rate_limits

   The Four Zone Heart Rate Limits characteristic is used to represent the limits
   between the heart rate zones for the four-zone heart rate definition
   (Maximum, Hard, Moderate, and Light) of a user.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> FourZoneHeartRateLimitsData

      Decode Four Zone Heart Rate Limits from raw bytes.

      :param data: Raw bytes from BLE characteristic (3 bytes)
      :param ctx: Optional context for parsing

      :returns: Parsed heart rate limits
      :rtype: FourZoneHeartRateLimitsData



   .. py:method:: encode_value(data: FourZoneHeartRateLimitsData) -> bytearray

      Encode Four Zone Heart Rate Limits to raw bytes.

      :param data: FourZoneHeartRateLimitsData to encode

      :returns: Encoded bytes
      :rtype: bytearray



   .. py:attribute:: expected_length
      :value: 3



.. py:class:: FourZoneHeartRateLimitsData

   Bases: :py:obj:`msgspec.Struct`


   Four Zone Heart Rate Limits data structure.


   .. py:attribute:: hard_maximum_limit
      :type:  int


   .. py:attribute:: light_moderate_limit
      :type:  int


   .. py:attribute:: moderate_hard_limit
      :type:  int


