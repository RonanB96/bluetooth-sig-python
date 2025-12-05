src.bluetooth_sig.gatt.characteristics.plx_features
===================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.plx_features

.. autoapi-nested-parse::

   PLX Features characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.plx_features.PLXFeatureFlags
   src.bluetooth_sig.gatt.characteristics.plx_features.PLXFeaturesCharacteristic


Module Contents
---------------

.. py:class:: PLXFeatureFlags

   Bases: :py:obj:`enum.IntFlag`


   PLX Features flags per Bluetooth SIG specification.

   Spec: Bluetooth SIG Assigned Numbers, PLX Features characteristic


   .. py:attribute:: MEASUREMENT_STATUS_SUPPORT
      :value: 1



   .. py:attribute:: DEVICE_AND_SENSOR_STATUS_SUPPORT
      :value: 2



   .. py:attribute:: MEASUREMENT_STORAGE_SUPPORT
      :value: 4



   .. py:attribute:: TIMESTAMP_SUPPORT
      :value: 8



   .. py:attribute:: SPO2PR_FAST_SUPPORT
      :value: 16



   .. py:attribute:: SPO2PR_SLOW_SUPPORT
      :value: 32



   .. py:attribute:: PULSE_AMPLITUDE_INDEX_SUPPORT
      :value: 64



   .. py:attribute:: MULTIPLE_BONDS_SUPPORT
      :value: 128



.. py:class:: PLXFeaturesCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   PLX Features characteristic (0x2A60).

   Describes the supported features of a pulse oximeter device.
   Returns a 16-bit feature flags value.

   Spec: Bluetooth SIG Assigned Numbers, PLX Features characteristic


   .. py:method:: decode_value(data: bytearray, ctx: bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> PLXFeatureFlags

      Decode PLX features from raw bytes.

      :param data: Raw bytes from BLE characteristic (2 bytes minimum)
      :param ctx: Unused, for signature compatibility

      :returns: PLXFeatureFlags enum with supported features

      :raises ValueError: If data length is less than 2 bytes



   .. py:method:: encode_value(data: PLXFeatureFlags | int) -> bytearray

      Encode PLX features to bytes.

      :param data: PLXFeatureFlags enum or 16-bit feature flags as integer

      :returns: Encoded bytes (2 bytes, little-endian)



