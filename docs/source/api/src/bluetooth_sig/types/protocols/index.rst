src.bluetooth_sig.types.protocols
=================================

.. py:module:: src.bluetooth_sig.types.protocols

.. autoapi-nested-parse::

   Protocol definitions for Bluetooth SIG standards.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.protocols.CharacteristicDataProtocol
   src.bluetooth_sig.types.protocols.CharacteristicProtocol


Module Contents
---------------

.. py:class:: CharacteristicDataProtocol

   Bases: :py:obj:`Protocol`


   Minimal protocol describing the attributes used by parsers.

   This avoids importing the full `CharacteristicData` type here and
   gives callers a useful static type for `other_characteristics`.

   Now includes field-level error reporting and parse trace capabilities
   for improved diagnostics.


   .. py:attribute:: field_errors
      :type:  list[Any]


   .. py:property:: name
      :type: str


      Characteristic name.


   .. py:attribute:: parse_success
      :type:  bool


   .. py:attribute:: parse_trace
      :type:  list[str]


   .. py:property:: properties
      :type: list[src.bluetooth_sig.types.gatt_enums.GattProperty]


      BLE GATT properties.


   .. py:attribute:: raw_data
      :type:  bytes


   .. py:attribute:: value
      :type:  Any


.. py:class:: CharacteristicProtocol

   Bases: :py:obj:`Protocol`


   Protocol for characteristic validation and round-trip testing.

   Defines the minimal interface for characteristics that support
   parse/encode operations without requiring full BaseCharacteristic import.
   Used primarily by debug utilities.


   .. py:method:: encode_value(value: Any) -> bytearray

      Encode characteristic value into raw data.



   .. py:method:: parse_value(data: bytearray) -> Any

      Parse raw data into characteristic value.



