src.bluetooth_sig.gatt.characteristics.supported_power_range
============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.supported_power_range

.. autoapi-nested-parse::

   Supported Power Range characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.supported_power_range.SupportedPowerRangeData
   src.bluetooth_sig.gatt.characteristics.supported_power_range.SupportedPowerRangeCharacteristic


Module Contents
---------------

.. py:class:: SupportedPowerRangeData

   Bases: :py:obj:`msgspec.Struct`


   Data class for supported power range.


   .. py:attribute:: minimum
      :type:  int


   .. py:attribute:: maximum
      :type:  int


.. py:class:: SupportedPowerRangeCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Supported Power Range characteristic (0x2AD8).

   org.bluetooth.characteristic.supported_power_range

   Supported Power Range characteristic.

   Specifies minimum and maximum power values for power capability
   specification.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> SupportedPowerRangeData

      Parse supported power range data (2x sint16 in watts).

      :param data: Raw bytes from the characteristic read.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: SupportedPowerRangeData with minimum and maximum power values in Watts.

      :raises ValueError: If data is insufficient.



   .. py:method:: encode_value(data: SupportedPowerRangeData) -> bytearray

      Encode supported power range value back to bytes.

      :param data: SupportedPowerRangeData instance with 'minimum' and 'maximum' power values in Watts

      :returns: Encoded bytes representing the power range (2x sint16)



