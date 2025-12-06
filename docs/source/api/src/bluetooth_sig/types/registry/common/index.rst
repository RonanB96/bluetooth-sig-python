src.bluetooth_sig.types.registry.common
=======================================

.. py:module:: src.bluetooth_sig.types.registry.common

.. autoapi-nested-parse::

   Core common types for Bluetooth SIG registry data structures.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.registry.common.BaseUuidInfo
   src.bluetooth_sig.types.registry.common.CharacteristicSpec
   src.bluetooth_sig.types.registry.common.FieldInfo
   src.bluetooth_sig.types.registry.common.KeyNameInfo
   src.bluetooth_sig.types.registry.common.NameOpcodeTypeInfo
   src.bluetooth_sig.types.registry.common.NameUuidTypeInfo
   src.bluetooth_sig.types.registry.common.NameValueInfo
   src.bluetooth_sig.types.registry.common.UnitMetadata
   src.bluetooth_sig.types.registry.common.UuidIdInfo
   src.bluetooth_sig.types.registry.common.ValueNameInfo
   src.bluetooth_sig.types.registry.common.ValueNameReferenceInfo


Functions
---------

.. autoapisummary::

   src.bluetooth_sig.types.registry.common.generate_basic_aliases


Module Contents
---------------

.. py:class:: BaseUuidInfo

   Bases: :py:obj:`msgspec.Struct`


   Minimal base info for all UUID-based registry entries.

   Child classes should add an id field as needed (required or optional).


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: uuid
      :type:  bluetooth_sig.types.uuid.BluetoothUUID


.. py:class:: CharacteristicSpec

   Bases: :py:obj:`msgspec.Struct`


   Characteristic specification from cross-file YAML references.


   .. py:property:: base_unit
      :type: str | None


      Get base unit from unit info.


   .. py:property:: data_type
      :type: str | None


      Get data type from field info.


   .. py:attribute:: description
      :type:  str | None
      :value: None



   .. py:attribute:: field_info
      :type:  FieldInfo


   .. py:property:: field_size
      :type: str | None


      Get field size from field info.


   .. py:attribute:: name
      :type:  str


   .. py:property:: resolution_text
      :type: str | None


      Get resolution text from unit info.


   .. py:property:: unit_id
      :type: str | None


      Get unit ID from unit info.


   .. py:attribute:: unit_info
      :type:  UnitMetadata


   .. py:property:: unit_symbol
      :type: str | None


      Get unit symbol from unit info.


   .. py:attribute:: uuid
      :type:  bluetooth_sig.types.uuid.BluetoothUUID


.. py:class:: FieldInfo

   Bases: :py:obj:`msgspec.Struct`


   Field-related metadata from YAML.


   .. py:attribute:: data_type
      :type:  str | None
      :value: None



   .. py:attribute:: description
      :type:  str | None
      :value: None



   .. py:attribute:: field_size
      :type:  str | None
      :value: None



   .. py:attribute:: name
      :type:  str | None
      :value: None



.. py:class:: KeyNameInfo

   Bases: :py:obj:`msgspec.Struct`


   Generic info for registries with key and name fields.

   Used by: security_keyIDs and similar registries with non-numeric keys.


   .. py:attribute:: key
      :type:  str


   .. py:attribute:: name
      :type:  str


.. py:class:: NameOpcodeTypeInfo

   Bases: :py:obj:`msgspec.Struct`


   Generic info for registries with name, opcode, and type fields.

   Used by: mesh opcodes and similar registries with opcode classification.


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: opcode
      :type:  int


   .. py:attribute:: type
      :type:  str


.. py:class:: NameUuidTypeInfo

   Bases: :py:obj:`BaseUuidInfo`


   Generic info for registries with name, uuid, and type fields.

   Used by: mesh model UUIDs and similar registries with type classification.
   Extends BaseUuidInfo to inherit uuid and name fields.


   .. py:attribute:: type
      :type:  str


.. py:class:: NameValueInfo

   Bases: :py:obj:`msgspec.Struct`


   Generic info for registries with name and value fields (reversed order).

   Used by: psm and similar registries where name comes before numeric value.


   .. py:attribute:: name
      :type:  str


   .. py:property:: psm
      :type: int


      Alias for value when used as PSM.


   .. py:attribute:: value
      :type:  int


.. py:class:: UnitMetadata

   Bases: :py:obj:`msgspec.Struct`


   Unit-related metadata from characteristic YAML specifications.

   This is embedded metadata within characteristic specs, distinct from
   the Units registry which uses UUID-based entries.


   .. py:attribute:: base_unit
      :type:  str | None
      :value: None



   .. py:attribute:: resolution_text
      :type:  str | None
      :value: None



   .. py:attribute:: unit_id
      :type:  str | None
      :value: None



   .. py:attribute:: unit_symbol
      :type:  str | None
      :value: None



.. py:class:: UuidIdInfo

   Bases: :py:obj:`BaseUuidInfo`


   Standard registry info for simple UUID-based registries with org.bluetooth ID.

   Extends BaseUuidInfo (uuid, name) with an id field for org.bluetooth identifiers.
   Used by registries with uuid, name, id fields:
   - browse_group_identifiers (uuid, name, id)
   - declarations (uuid, name, id)
   ...


   .. py:attribute:: id
      :type:  str


.. py:class:: ValueNameInfo

   Bases: :py:obj:`msgspec.Struct`


   Generic info for registries with value and name fields.

   Used by: coding_format, core_version, diacs, mws_channel_type,
   namespace, namespaces, pcm_data_format, transport_layers, uri_schemes,
   company_identifiers, and many others.


   .. py:property:: bit
      :type: int


      Alias for value when used as bit position.


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: value
      :type:  int


.. py:class:: ValueNameReferenceInfo

   Bases: :py:obj:`msgspec.Struct`


   Generic info for registries with value, name, and reference fields.

   Used by: ad_types and similar registries with specification references.


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: reference
      :type:  str


   .. py:attribute:: value
      :type:  int


.. py:function:: generate_basic_aliases(info: BaseUuidInfo) -> set[str]

   Generate a small set of common alias keys for a BaseUuidInfo.

   Domain-specific heuristics remain the responsibility of the registry.


