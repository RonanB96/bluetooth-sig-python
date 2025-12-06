src.bluetooth_sig.types.io
==========================

.. py:module:: src.bluetooth_sig.types.io

.. autoapi-nested-parse::

   Typed containers for staging raw BLE I/O into the translator.

   These structs model common outputs from BLE connection managers (e.g., Bleak,
   SimpleBLE) and provide a convenient way to feed raw bytes into the
   `BluetoothSIGTranslator` batch parser, including descriptor bytes when
   available.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.io.RawCharacteristicBatch
   src.bluetooth_sig.types.io.RawCharacteristicRead


Functions
---------

.. autoapisummary::

   src.bluetooth_sig.types.io.to_parse_inputs


Module Contents
---------------

.. py:class:: RawCharacteristicBatch

   Bases: :py:obj:`msgspec.Struct`


   A batch of raw characteristic reads to be parsed together.

   Use this when you have multiple related characteristics (e.g., Glucose
   Measurement + Glucose Measurement Context). The translator can parse them in
   dependency-aware order.


   .. py:attribute:: items
      :type:  list[RawCharacteristicRead]


.. py:class:: RawCharacteristicRead

   Bases: :py:obj:`msgspec.Struct`


   Container for a single characteristic read.

   This type is convenient for users to stage raw values coming from their BLE
   connection manager (e.g. Bleak, SimpleBLE) before handing them to the
   translator. It models the common shape produced by those libraries:

   - `uuid`: characteristic UUID (short or full form)
   - `raw_data`: bytes value as returned by `read_gatt_char`/notification
   - `descriptors`: optional mapping of descriptor UUID -> raw bytes (if read)
   - `properties`: optional list of characteristic properties (e.g. "read",
     "notify"). These are currently informational for the parser.


   .. py:attribute:: descriptors
      :type:  dict[str, bytes]


   .. py:attribute:: properties
      :type:  list[str]


   .. py:attribute:: raw_data
      :type:  bytes


   .. py:attribute:: uuid
      :type:  src.bluetooth_sig.types.uuid.BluetoothUUID | str


.. py:function:: to_parse_inputs(batch: RawCharacteristicBatch) -> tuple[dict[str, bytes], dict[str, dict[str, bytes]]]

   Convert a :class:`RawCharacteristicBatch` to translator inputs.

   Returns a tuple of `(char_data, descriptor_data)` suitable for
   `BluetoothSIGTranslator.parse_characteristics(char_data, descriptor_data=...)`.

   - `char_data` is a mapping of UUID -> raw bytes
   - `descriptor_data` is a nested mapping of char UUID -> (descriptor UUID -> raw bytes)


