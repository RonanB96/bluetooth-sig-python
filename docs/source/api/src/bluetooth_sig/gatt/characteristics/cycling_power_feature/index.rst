src.bluetooth_sig.gatt.characteristics.cycling_power_feature
============================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.cycling_power_feature

.. autoapi-nested-parse::

   Cycling Power Feature characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.cycling_power_feature.CyclingPowerFeatureCharacteristic
   src.bluetooth_sig.gatt.characteristics.cycling_power_feature.CyclingPowerFeatureData
   src.bluetooth_sig.gatt.characteristics.cycling_power_feature.CyclingPowerFeatures


Module Contents
---------------

.. py:class:: CyclingPowerFeatureCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Cycling Power Feature characteristic (0x2A65).

   Used to expose the supported features of a cycling power sensor.
   Contains a 32-bit bitmask indicating supported measurement
   capabilities.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> CyclingPowerFeatureData

      Parse cycling power feature data.

      Format: 32-bit feature bitmask (little endian).

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: CyclingPowerFeatureData containing parsed feature flags.

      :raises ValueError: If data format is invalid.



   .. py:method:: encode_value(data: CyclingPowerFeatureData) -> bytearray

      Encode cycling power feature value back to bytes.

      :param data: CyclingPowerFeatureData containing cycling power feature data

      :returns: Encoded bytes representing the cycling power features (uint32)



.. py:class:: CyclingPowerFeatureData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from Cycling Power Feature characteristic.


   .. py:attribute:: accumulated_energy_supported
      :type:  bool


   .. py:attribute:: crank_revolution_data_supported
      :type:  bool


   .. py:attribute:: features
      :type:  CyclingPowerFeatures


   .. py:attribute:: pedal_power_balance_supported
      :type:  bool


   .. py:attribute:: wheel_revolution_data_supported
      :type:  bool


.. py:class:: CyclingPowerFeatures

   Bases: :py:obj:`enum.IntFlag`


   Cycling Power Feature flags as per Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: ACCUMULATED_ENERGY_SUPPORTED
      :value: 2



   .. py:attribute:: CRANK_REVOLUTION_DATA_SUPPORTED
      :value: 8



   .. py:attribute:: PEDAL_POWER_BALANCE_SUPPORTED
      :value: 1



   .. py:attribute:: WHEEL_REVOLUTION_DATA_SUPPORTED
      :value: 4



