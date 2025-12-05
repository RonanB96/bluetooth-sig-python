src.bluetooth_sig.gatt.characteristics.generic_access
=====================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.generic_access

.. autoapi-nested-parse::

   Generic Access Service characteristics.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.generic_access.ServiceChangedData
   src.bluetooth_sig.gatt.characteristics.generic_access.DeviceNameCharacteristic
   src.bluetooth_sig.gatt.characteristics.generic_access.AppearanceCharacteristic
   src.bluetooth_sig.gatt.characteristics.generic_access.ServiceChangedCharacteristic


Module Contents
---------------

.. py:class:: ServiceChangedData

   Bases: :py:obj:`msgspec.Struct`


   Service Changed characteristic data.

   .. attribute:: start_handle

      Starting handle of the affected service range

   .. attribute:: end_handle

      Ending handle of the affected service range


   .. py:attribute:: start_handle
      :type:  int


   .. py:attribute:: end_handle
      :type:  int


.. py:class:: DeviceNameCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Device Name characteristic (0x2A00).

   org.bluetooth.characteristic.gap.device_name

   Device Name characteristic.


.. py:class:: AppearanceCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Appearance characteristic (0x2A01).

   org.bluetooth.characteristic.gap.appearance

   Appearance characteristic with human-readable device type information.


   .. py:attribute:: min_length
      :value: 2



   .. py:attribute:: max_length
      :value: 2



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: False



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> src.bluetooth_sig.types.appearance.AppearanceData

      Parse appearance value with human-readable info.

      :param data: Raw bytearray from BLE characteristic (2 bytes).
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: AppearanceData with raw value and optional human-readable info.

      .. admonition:: Example

         >>> char = AppearanceCharacteristic()
         >>> result = char.decode_value(bytearray([0x41, 0x03]))  # 833
         >>> print(result.full_name)  # "Heart Rate Sensor: Heart Rate Belt"
         >>> print(result.raw_value)  # 833
         >>> print(int(result))  # 833



   .. py:method:: encode_value(data: src.bluetooth_sig.types.appearance.AppearanceData) -> bytearray

      Encode appearance value back to bytes.

      :param data: Appearance value as AppearanceData

      :returns: Encoded bytes representing the appearance



.. py:class:: ServiceChangedCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Service Changed characteristic (0x2A05).

   org.bluetooth.characteristic.gatt.service_changed

   Service Changed characteristic.


   .. py:attribute:: min_length
      :value: 4



   .. py:attribute:: max_length
      :value: 4



   .. py:attribute:: allow_variable_length
      :type:  bool
      :value: False



   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> ServiceChangedData

      Parse service changed value.

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: ServiceChangedData with start_handle and end_handle.

      :raises ValueError: If data length is not exactly 4 bytes.



   .. py:method:: encode_value(data: ServiceChangedData) -> bytearray

      Encode service changed value back to bytes.

      :param data: ServiceChangedData with start_handle and end_handle

      :returns: Encoded bytes



