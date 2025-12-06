src.bluetooth_sig.gatt.characteristics.three_zone_heart_rate_limits
===================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.three_zone_heart_rate_limits

.. autoapi-nested-parse::

   Three Zone Heart Rate Limits characteristic (0x2A94).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.three_zone_heart_rate_limits.ThreeZoneHeartRateLimitsCharacteristic
   src.bluetooth_sig.gatt.characteristics.three_zone_heart_rate_limits.ThreeZoneHeartRateLimitsData


Module Contents
---------------

.. py:class:: ThreeZoneHeartRateLimitsCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Three Zone Heart Rate Limits characteristic (0x2A94).

   org.bluetooth.characteristic.three_zone_heart_rate_limits

   The Three Zone Heart Rate Limits characteristic is used to represent the limits
   between the heart rate zones for the three-zone heart rate definition
   (Hard, Moderate, and Light) of a user.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> ThreeZoneHeartRateLimitsData

      Decode Three Zone Heart Rate Limits from raw bytes.

      :param data: Raw bytes from BLE characteristic (2 bytes)
      :param ctx: Optional context for parsing

      :returns: Parsed heart rate limits
      :rtype: ThreeZoneHeartRateLimitsData



   .. py:method:: encode_value(data: ThreeZoneHeartRateLimitsData) -> bytearray

      Encode Three Zone Heart Rate Limits to raw bytes.

      :param data: ThreeZoneHeartRateLimitsData to encode

      :returns: Encoded bytes
      :rtype: bytearray



   .. py:attribute:: expected_length
      :value: 2



.. py:class:: ThreeZoneHeartRateLimitsData

   Bases: :py:obj:`msgspec.Struct`


   Three Zone Heart Rate Limits data structure.


   .. py:attribute:: light_moderate_limit
      :type:  int


   .. py:attribute:: moderate_hard_limit
      :type:  int


