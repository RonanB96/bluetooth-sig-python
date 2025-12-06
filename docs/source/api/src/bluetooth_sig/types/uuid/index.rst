src.bluetooth_sig.types.uuid
============================

.. py:module:: src.bluetooth_sig.types.uuid

.. autoapi-nested-parse::

   Bluetooth UUID utilities for handling 16-bit and 128-bit UUIDs.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.uuid.BluetoothUUID


Module Contents
---------------

.. py:class:: BluetoothUUID(uuid: str | int | BluetoothUUID)

   Bluetooth UUID class that handles both 16-bit and 128-bit UUIDs with automatic normalization and conversion.

   Supports various input formats:
   - Short form: "180F", "0x180F", "180f"
   - Full form: "0000180F-0000-1000-8000-00805F9B34FB"
   - Normalized: "0000180F00001000800000805F9B34FB"
   - Integer: 6159 (for 16-bit) or large integer (for 128-bit)

   Provides automatic conversion between formats and consistent comparison.

   Initialize BluetoothUUID from a UUID string or integer.

   :param uuid: UUID string in any valid format (short, full, dashed, hex-prefixed) or integer

   :raises ValueError: If UUID format is invalid


   .. py:method:: is_sig_characteristic() -> bool

      Check if this UUID is a Bluetooth SIG assigned characteristic UUID.

      Based on actual SIG assigned numbers from characteristic_uuids.yaml.
      Range verified: 0x2A00 to 0x2C24 (and potentially expanding).

      :returns: True if this is a SIG characteristic UUID, False otherwise



   .. py:method:: is_sig_service() -> bool

      Check if this UUID is a Bluetooth SIG assigned service UUID.

      Based on actual SIG assigned numbers from service_uuids.yaml.
      Range verified: 0x1800 to 0x185C (and potentially expanding).

      :returns: True if this is a SIG service UUID, False otherwise



   .. py:method:: is_valid_for_custom_characteristic() -> bool

      Check if this UUID is valid for custom characteristics.

      :returns:

                - Base UUID (00000000-0000-1000-8000-00805f9b34fb)
                - Null UUID (all zeros)
                - Placeholder UUID (used internally)
                True otherwise
      :rtype: False if the UUID is any of the invalid/reserved UUIDs



   .. py:method:: matches(other: str | BluetoothUUID) -> bool

      Check if this UUID matches another UUID (handles format conversion automatically).



   .. py:attribute:: BASE_UUID
      :value: '0000XXXX00001000800000805F9B34FB'



   .. py:attribute:: INVALID_BASE_UUID_DASHED
      :value: '00000000-0000-1000-8000-00805f9b34fb'



   .. py:attribute:: INVALID_BASE_UUID_NORMALIZED
      :value: '0000000000001000800000805F9B34FB'



   .. py:attribute:: INVALID_NULL_UUID
      :value: '0000000000000000000000000000'



   .. py:attribute:: INVALID_PLACEHOLDER_UUID
      :value: '0000123400001000800000805F9B34FB'



   .. py:attribute:: INVALID_SHORT_UUID
      :value: '0000'



   .. py:attribute:: SIG_BASE_SUFFIX
      :value: '00001000800000805F9B34FB'



   .. py:attribute:: SIG_CHARACTERISTIC_MAX
      :value: 11300



   .. py:attribute:: SIG_CHARACTERISTIC_MIN
      :value: 10752



   .. py:attribute:: SIG_SERVICE_MAX
      :value: 6236



   .. py:attribute:: SIG_SERVICE_MIN
      :value: 6144



   .. py:attribute:: UUID_FULL_LEN
      :value: 32



   .. py:attribute:: UUID_SHORT_LEN
      :value: 4



   .. py:property:: bytes
      :type: bytes


      Get UUID as 16-byte binary representation (big-endian).

      Useful for BLE wire protocol operations where UUIDs need to be
      transmitted in binary format.

      :returns: 16 bytes representing the full 128-bit UUID in big-endian byte order


   .. py:property:: bytes_le
      :type: bytes


      Get UUID as 16-byte binary representation (little-endian).

      Some BLE operations require little-endian byte order.

      :returns: 16 bytes representing the full 128-bit UUID in little-endian byte order


   .. py:property:: dashed_form
      :type: str


      Get UUID in standard dashed format (e.g., '0000180F-0000-1000-8000-00805F9B34FB').


   .. py:property:: full_form
      :type: str


      Get 128-bit full form with Bluetooth base UUID.


   .. py:property:: int_value
      :type: int


      Get UUID as integer value.


   .. py:property:: is_full
      :type: bool


      Check if this is a 128-bit (full) UUID.


   .. py:property:: is_short
      :type: bool


      Check if this is a 16-bit (short) UUID.


   .. py:property:: normalized
      :type: str


      Get normalized UUID (uppercase hex, no dashes, no 0x prefix).


   .. py:property:: short_form
      :type: str


      Get 16-bit short form (e.g., '180F').


