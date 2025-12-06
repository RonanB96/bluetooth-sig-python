src.bluetooth_sig.gatt.characteristics.reference_time_information
=================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.reference_time_information

.. autoapi-nested-parse::

   Reference Time Information characteristic (0x2A14) implementation.

   Provides information about the reference time source, including its type,
   accuracy, and time since last update.

   Based on Bluetooth SIG GATT Specification:
   - Reference Time Information: 4 bytes (Time Source + Time Accuracy + Days Since Update + Hours Since Update)
   - Time Source: uint8 (0=Unknown, 1=NTP, 2=GPS, etc.)
   - Time Accuracy: uint8 (0-253 in 125ms steps, 254=out of range, 255=unknown)
   - Days Since Update: uint8 (0-254, 255 means >=255 days)
   - Hours Since Update: uint8 (0-23, 255 means >=255 days)



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.reference_time_information.HOURS_SINCE_UPDATE_MAX
   src.bluetooth_sig.gatt.characteristics.reference_time_information.HOURS_SINCE_UPDATE_OUT_OF_RANGE
   src.bluetooth_sig.gatt.characteristics.reference_time_information.REFERENCE_TIME_INFO_LENGTH
   src.bluetooth_sig.gatt.characteristics.reference_time_information.TIME_SOURCE_MAX


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.reference_time_information.ReferenceTimeInformationCharacteristic
   src.bluetooth_sig.gatt.characteristics.reference_time_information.ReferenceTimeInformationData
   src.bluetooth_sig.gatt.characteristics.reference_time_information.TimeSource


Module Contents
---------------

.. py:class:: ReferenceTimeInformationCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Reference Time Information characteristic (0x2A14).

   Represents information about the reference time source including type,
   accuracy, and time elapsed since last synchronization.

   Structure (4 bytes):
   - Time Source: uint8 (0=Unknown, 1=NTP, 2=GPS, 3=Radio, 4=Manual, 5=Atomic, 6=Cellular, 7=Not Sync)
   - Time Accuracy: uint8 (0-253 in 125ms steps, 254=out of range >31.625s, 255=unknown)
   - Days Since Update: uint8 (0-254 days, 255 means >=255 days)
   - Hours Since Update: uint8 (0-23 hours, 255 means >=255 days)

   Used by Current Time Service (0x1805).

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> ReferenceTimeInformationData

      Decode Reference Time Information data from bytes.

      :param data: Raw characteristic data (4 bytes)
      :param ctx: Optional characteristic context

      :returns: ReferenceTimeInformationData with all fields

      :raises ValueError: If data is insufficient or contains invalid values



   .. py:method:: encode_value(data: ReferenceTimeInformationData) -> bytearray

      Encode Reference Time Information data to bytes.

      :param data: ReferenceTimeInformationData to encode

      :returns: Encoded reference time information (4 bytes)

      :raises ValueError: If data contains invalid values



.. py:class:: ReferenceTimeInformationData

   Bases: :py:obj:`msgspec.Struct`


   Reference Time Information characteristic data structure.


   .. py:attribute:: days_since_update
      :type:  int


   .. py:attribute:: hours_since_update
      :type:  int


   .. py:attribute:: time_accuracy
      :type:  int


   .. py:attribute:: time_source
      :type:  TimeSource


.. py:class:: TimeSource

   Bases: :py:obj:`enum.IntEnum`


   Time source enumeration per Bluetooth SIG specification.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: ATOMIC_CLOCK
      :value: 5



   .. py:attribute:: CELLULAR_NETWORK
      :value: 6



   .. py:attribute:: GPS
      :value: 2



   .. py:attribute:: MANUAL
      :value: 4



   .. py:attribute:: NETWORK_TIME_PROTOCOL
      :value: 1



   .. py:attribute:: NOT_SYNCHRONIZED
      :value: 7



   .. py:attribute:: RADIO_TIME_SIGNAL
      :value: 3



   .. py:attribute:: UNKNOWN
      :value: 0



.. py:data:: HOURS_SINCE_UPDATE_MAX
   :value: 23


.. py:data:: HOURS_SINCE_UPDATE_OUT_OF_RANGE
   :value: 255


.. py:data:: REFERENCE_TIME_INFO_LENGTH
   :value: 4


.. py:data:: TIME_SOURCE_MAX
   :value: 7


