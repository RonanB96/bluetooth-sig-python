src.bluetooth_sig.gatt.characteristics.voltage_statistics
=========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.voltage_statistics

.. autoapi-nested-parse::

   Voltage Statistics characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.voltage_statistics.VoltageStatisticsCharacteristic
   src.bluetooth_sig.gatt.characteristics.voltage_statistics.VoltageStatisticsData


Module Contents
---------------

.. py:class:: VoltageStatisticsCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Voltage Statistics characteristic (0x2B1A).

   org.bluetooth.characteristic.voltage_statistics

   Voltage Statistics characteristic.

   Provides statistical voltage data over time.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> VoltageStatisticsData

      Parse voltage statistics data (3x uint16 in units of 1/64 V).

      :param data: Raw bytes from the characteristic read.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: VoltageStatisticsData with 'minimum', 'maximum', and 'average' voltage values in Volts.

      # `ctx` is intentionally unused for this characteristic; mark as used for linters.
      del ctx
      :raises ValueError: If data is insufficient.



   .. py:method:: encode_value(data: VoltageStatisticsData) -> bytearray

      Encode voltage statistics value back to bytes.

      :param data: VoltageStatisticsData instance with 'minimum', 'maximum', and 'average' voltage values in Volts

      :returns: Encoded bytes representing the voltage statistics (3x uint16, 1/64 V resolution)



.. py:class:: VoltageStatisticsData

   Bases: :py:obj:`msgspec.Struct`


   Data class for voltage statistics.


   .. py:attribute:: average
      :type:  float


   .. py:attribute:: maximum
      :type:  float


   .. py:attribute:: minimum
      :type:  float


