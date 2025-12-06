src.bluetooth_sig.gatt.characteristics.electric_current_statistics
==================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.electric_current_statistics

.. autoapi-nested-parse::

   Electric Current Statistics characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.electric_current_statistics.ElectricCurrentStatisticsCharacteristic
   src.bluetooth_sig.gatt.characteristics.electric_current_statistics.ElectricCurrentStatisticsData


Module Contents
---------------

.. py:class:: ElectricCurrentStatisticsCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Electric Current Statistics characteristic (0x2AF1).

   org.bluetooth.characteristic.electric_current_statistics

   Electric Current Statistics characteristic.

   Provides statistical current data (min, max, average over time).

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> ElectricCurrentStatisticsData

      Parse current statistics data (3x uint16 in units of 0.01 A).

      :param data: Raw bytes from the characteristic read.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: ElectricCurrentStatisticsData with 'minimum', 'maximum', and 'average' current values in Amperes.

      :raises ValueError: If data is insufficient.



   .. py:method:: encode_value(data: ElectricCurrentStatisticsData) -> bytearray

      Encode electric current statistics value back to bytes.

      :param data: ElectricCurrentStatisticsData instance

      :returns: Encoded bytes representing the current statistics (3x uint16, 0.01 A resolution)



.. py:class:: ElectricCurrentStatisticsData

   Bases: :py:obj:`msgspec.Struct`


   Data class for electric current statistics.


   .. py:attribute:: average
      :type:  float


   .. py:attribute:: maximum
      :type:  float


   .. py:attribute:: minimum
      :type:  float


