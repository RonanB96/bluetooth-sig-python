src.bluetooth_sig.gatt.characteristics.csc_feature
==================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.csc_feature

.. autoapi-nested-parse::

   CSC Feature characteristic implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.csc_feature.CSCFeatures
   src.bluetooth_sig.gatt.characteristics.csc_feature.CSCFeatureData
   src.bluetooth_sig.gatt.characteristics.csc_feature.CSCFeatureCharacteristic


Module Contents
---------------

.. py:class:: CSCFeatures

   Bases: :py:obj:`enum.IntFlag`


   CSC Feature flags as per Bluetooth SIG specification.


   .. py:attribute:: WHEEL_REVOLUTION_DATA_SUPPORTED
      :value: 1



   .. py:attribute:: CRANK_REVOLUTION_DATA_SUPPORTED
      :value: 2



   .. py:attribute:: MULTIPLE_SENSOR_LOCATIONS_SUPPORTED
      :value: 4



.. py:class:: CSCFeatureData

   Bases: :py:obj:`msgspec.Struct`


   Parsed data from CSC Feature characteristic.


   .. py:attribute:: features
      :type:  CSCFeatures


   .. py:attribute:: wheel_revolution_data_supported
      :type:  bool


   .. py:attribute:: crank_revolution_data_supported
      :type:  bool


   .. py:attribute:: multiple_sensor_locations_supported
      :type:  bool


.. py:class:: CSCFeatureCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   CSC Feature characteristic (0x2A5C).

   Used to expose the supported features of a CSC sensor.
   Contains a 16-bit bitmask indicating supported measurement
   capabilities.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> CSCFeatureData

      Parse CSC feature data.

      Format: 16-bit feature bitmask (little endian).

      :param data: Raw bytearray from BLE characteristic.
      :param ctx: Optional CharacteristicContext providing surrounding context (may be None).

      :returns: CSCFeatureData containing parsed feature flags.

      :raises ValueError: If data format is invalid.



   .. py:method:: encode_value(data: CSCFeatureData) -> bytearray

      Encode CSC feature value back to bytes.

      :param data: CSCFeatureData containing CSC feature data

      :returns: Encoded bytes representing the CSC features (uint16)



