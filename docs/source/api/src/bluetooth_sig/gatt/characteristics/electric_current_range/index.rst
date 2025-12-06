src.bluetooth_sig.gatt.characteristics.electric_current_range
=============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.electric_current_range

.. autoapi-nested-parse::

   Electric Current Range characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.electric_current_range.ElectricCurrentRangeCharacteristic
   src.bluetooth_sig.gatt.characteristics.electric_current_range.ElectricCurrentRangeData


Module Contents
---------------

.. py:class:: ElectricCurrentRangeCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Electric Current Range characteristic (0x2AEF).

   org.bluetooth.characteristic.electric_current_range

   Electric Current Range characteristic.

   Specifies lower and upper current bounds (2x uint16).

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> ElectricCurrentRangeData

      Parse current range data (2x uint16 in units of 0.01 A).

      :param data: Raw bytes from the characteristic read.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: ElectricCurrentRangeData with 'min' and 'max' current values in Amperes.

      :raises ValueError: If data is insufficient.



   .. py:method:: encode_value(data: ElectricCurrentRangeData) -> bytearray

      Encode electric current range value back to bytes.

      :param data: ElectricCurrentRangeData instance with 'min' and 'max' current values in Amperes

      :returns: Encoded bytes representing the current range (2x uint16, 0.01 A resolution)



.. py:class:: ElectricCurrentRangeData

   Bases: :py:obj:`msgspec.Struct`


   Data class for electric current range.


   .. py:attribute:: max
      :type:  float


   .. py:attribute:: min
      :type:  float


