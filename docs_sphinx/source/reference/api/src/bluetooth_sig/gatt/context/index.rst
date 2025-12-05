src.bluetooth_sig.gatt.context
==============================

.. py:module:: src.bluetooth_sig.gatt.context

.. autoapi-nested-parse::

   Context objects used during characteristic parsing.

   This module provides a small, well-typed container that parsers can use
   to access device-level information, advertisement data, and already-
   parsed characteristics when decoding values that depend on context.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.context.CharacteristicContext
   src.bluetooth_sig.gatt.context.CharacteristicDataProtocol
   src.bluetooth_sig.gatt.context.DeviceInfo


Module Contents
---------------

.. py:class:: CharacteristicContext

   Bases: :py:obj:`msgspec.Struct`


   Runtime context passed into parsers - INPUT only.

   This provides the parsing context (device info, other characteristics for
   dependencies, etc.) but does NOT contain output fields. Descriptors have
   their own separate parsing flow.

   .. attribute:: device_info

      Basic device metadata (address, name, manufacturer data).

   .. attribute:: advertisement

      Raw advertisement bytes if available.

   .. attribute:: other_characteristics

      Mapping from characteristic UUID string to
      previously-parsed characteristic result. Parsers may consult this
      mapping to implement multi-characteristic decoding.

   .. attribute:: descriptors

      Mapping from descriptor UUID string to parsed descriptor data.
      Provides access to characteristic descriptors during parsing.

   .. attribute:: raw_service

      Optional raw service-level payload when applicable.


   .. py:attribute:: device_info
      :type:  DeviceInfo | None
      :value: None



   .. py:attribute:: advertisement
      :type:  bytes
      :value: b''



   .. py:attribute:: other_characteristics
      :type:  collections.abc.Mapping[str, src.bluetooth_sig.types.protocols.CharacteristicDataProtocol] | None
      :value: None



   .. py:attribute:: descriptors
      :type:  collections.abc.Mapping[str, src.bluetooth_sig.types.registry.descriptor_types.DescriptorData] | None
      :value: None



   .. py:attribute:: raw_service
      :type:  bytes
      :value: b''



.. py:class:: CharacteristicDataProtocol

   Bases: :py:obj:`Protocol`


   Minimal protocol describing the attributes used by parsers.

   This avoids importing the full `CharacteristicData` type here and
   gives callers a useful static type for `other_characteristics`.

   Now includes field-level error reporting and parse trace capabilities
   for improved diagnostics.


   .. py:attribute:: value
      :type:  Any


   .. py:attribute:: raw_data
      :type:  bytes


   .. py:attribute:: parse_success
      :type:  bool


   .. py:property:: properties
      :type: list[src.bluetooth_sig.types.gatt_enums.GattProperty]


      BLE GATT properties.


   .. py:property:: name
      :type: str


      Characteristic name.


   .. py:attribute:: field_errors
      :type:  list[Any]


   .. py:attribute:: parse_trace
      :type:  list[str]


.. py:class:: DeviceInfo

   Bases: :py:obj:`msgspec.Struct`


   Basic device metadata available to parsers.


   .. py:attribute:: address
      :type:  str
      :value: ''



   .. py:attribute:: name
      :type:  str
      :value: ''



   .. py:attribute:: manufacturer_data
      :type:  dict[int, bytes]


   .. py:attribute:: service_uuids
      :type:  list[str]


