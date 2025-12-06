src.bluetooth_sig.types.context
===============================

.. py:module:: src.bluetooth_sig.types.context

.. autoapi-nested-parse::

   Context objects used during characteristic parsing.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.context.CharacteristicContext
   src.bluetooth_sig.types.context.DeviceInfo


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


   .. py:attribute:: advertisement
      :type:  bytes
      :value: b''



   .. py:attribute:: descriptors
      :type:  collections.abc.Mapping[str, src.bluetooth_sig.types.registry.descriptor_types.DescriptorData] | None
      :value: None



   .. py:attribute:: device_info
      :type:  DeviceInfo | None
      :value: None



   .. py:attribute:: other_characteristics
      :type:  collections.abc.Mapping[str, src.bluetooth_sig.types.protocols.CharacteristicDataProtocol] | None
      :value: None



   .. py:attribute:: raw_service
      :type:  bytes
      :value: b''



.. py:class:: DeviceInfo

   Bases: :py:obj:`msgspec.Struct`


   Basic device metadata available to parsers.


   .. py:attribute:: address
      :type:  str
      :value: ''



   .. py:attribute:: manufacturer_data
      :type:  dict[int, bytes]


   .. py:attribute:: name
      :type:  str
      :value: ''



   .. py:attribute:: service_uuids
      :type:  list[str]


