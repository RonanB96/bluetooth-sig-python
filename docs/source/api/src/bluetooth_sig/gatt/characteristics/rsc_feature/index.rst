src.bluetooth_sig.gatt.characteristics.rsc_feature
==================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.rsc_feature

.. autoapi-nested-parse::

   RSC Feature characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.rsc_feature.RSCFeatureCharacteristic
   src.bluetooth_sig.gatt.characteristics.rsc_feature.RSCFeatureData
   src.bluetooth_sig.gatt.characteristics.rsc_feature.RSCFeatures


Module Contents
---------------

.. py:class:: RSCFeatureCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   RSC Feature characteristic (0x2A54).

   Used to expose the supported features of an RSC sensor.
   Contains a 16-bit bitmask indicating supported measurement
   capabilities.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> RSCFeatureData

      Parse RSC feature data.

      Format: 16-bit feature bitmask (little endian).

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: RSCFeatureData containing parsed feature flags.

      :raises ValueError: If data format is invalid.



   .. py:method:: encode_value(data: RSCFeatureData) -> bytearray

      Encode RSC feature value back to bytes.

      :param data: RSCFeatureData containing RSC feature data

      :returns: Encoded bytes representing the RSC features (uint16)



.. py:class:: RSCFeatureData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from RSC Feature characteristic.


   .. py:attribute:: calibration_procedure_supported
      :type:  bool


   .. py:attribute:: features
      :type:  RSCFeatures


   .. py:attribute:: instantaneous_stride_length_supported
      :type:  bool


   .. py:attribute:: multiple_sensor_locations_supported
      :type:  bool


   .. py:attribute:: total_distance_supported
      :type:  bool


   .. py:attribute:: walking_or_running_status_supported
      :type:  bool


.. py:class:: RSCFeatures

   Bases: :py:obj:`enum.IntFlag`


   RSC Feature flags as per Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: CALIBRATION_PROCEDURE_SUPPORTED
      :value: 8



   .. py:attribute:: INSTANTANEOUS_STRIDE_LENGTH_SUPPORTED
      :value: 1



   .. py:attribute:: MULTIPLE_SENSOR_LOCATIONS_SUPPORTED
      :value: 16



   .. py:attribute:: TOTAL_DISTANCE_SUPPORTED
      :value: 2



   .. py:attribute:: WALKING_OR_RUNNING_STATUS_SUPPORTED
      :value: 4



