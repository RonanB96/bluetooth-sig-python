src.bluetooth_sig.types.registry
================================

.. py:module:: src.bluetooth_sig.types.registry

.. autoapi-nested-parse::

   Core types for Bluetooth SIG registry data structures.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /reference/api/src/bluetooth_sig/types/registry/ad_types/index
   /reference/api/src/bluetooth_sig/types/registry/amp/index
   /reference/api/src/bluetooth_sig/types/registry/appearance_info/index
   /reference/api/src/bluetooth_sig/types/registry/browse_group_identifiers/index
   /reference/api/src/bluetooth_sig/types/registry/characteristic_uuids/index
   /reference/api/src/bluetooth_sig/types/registry/class_of_device/index
   /reference/api/src/bluetooth_sig/types/registry/coding_format/index
   /reference/api/src/bluetooth_sig/types/registry/common/index
   /reference/api/src/bluetooth_sig/types/registry/company_identifiers/index
   /reference/api/src/bluetooth_sig/types/registry/core_version/index
   /reference/api/src/bluetooth_sig/types/registry/declarations/index
   /reference/api/src/bluetooth_sig/types/registry/descriptor_types/index
   /reference/api/src/bluetooth_sig/types/registry/descriptors/index
   /reference/api/src/bluetooth_sig/types/registry/diacs/index
   /reference/api/src/bluetooth_sig/types/registry/dp_property/index
   /reference/api/src/bluetooth_sig/types/registry/dp_property_groups/index
   /reference/api/src/bluetooth_sig/types/registry/dp_property_ids/index
   /reference/api/src/bluetooth_sig/types/registry/formattypes/index
   /reference/api/src/bluetooth_sig/types/registry/gss_characteristic/index
   /reference/api/src/bluetooth_sig/types/registry/member_uuids/index
   /reference/api/src/bluetooth_sig/types/registry/mesh_profile_uuids/index
   /reference/api/src/bluetooth_sig/types/registry/mws_channel_type/index
   /reference/api/src/bluetooth_sig/types/registry/namespace/index
   /reference/api/src/bluetooth_sig/types/registry/namespaces/index
   /reference/api/src/bluetooth_sig/types/registry/object_types/index
   /reference/api/src/bluetooth_sig/types/registry/pcm_data_format/index
   /reference/api/src/bluetooth_sig/types/registry/protocol_identifiers/index
   /reference/api/src/bluetooth_sig/types/registry/psm/index
   /reference/api/src/bluetooth_sig/types/registry/sdo_uuids/index
   /reference/api/src/bluetooth_sig/types/registry/sdp_base_uuid/index
   /reference/api/src/bluetooth_sig/types/registry/service_class/index
   /reference/api/src/bluetooth_sig/types/registry/service_uuids/index
   /reference/api/src/bluetooth_sig/types/registry/transport_layers/index
   /reference/api/src/bluetooth_sig/types/registry/units/index
   /reference/api/src/bluetooth_sig/types/registry/uri_schemes/index


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.registry.BaseUuidInfo
   src.bluetooth_sig.types.registry.CharacteristicSpec
   src.bluetooth_sig.types.registry.FieldInfo
   src.bluetooth_sig.types.registry.KeyNameInfo
   src.bluetooth_sig.types.registry.NameOpcodeTypeInfo
   src.bluetooth_sig.types.registry.NameUuidTypeInfo
   src.bluetooth_sig.types.registry.NameValueInfo
   src.bluetooth_sig.types.registry.UnitMetadata
   src.bluetooth_sig.types.registry.UuidIdInfo
   src.bluetooth_sig.types.registry.ValueNameInfo
   src.bluetooth_sig.types.registry.ValueNameReferenceInfo


Functions
---------

.. autoapisummary::

   src.bluetooth_sig.types.registry.generate_basic_aliases


Package Contents
----------------

.. py:class:: BaseUuidInfo

   Bases: :py:obj:`msgspec.Struct`


   Minimal base info for all UUID-based registry entries.

   Child classes should add an id field as needed (required or optional).


   .. py:attribute:: uuid
      :type:  bluetooth_sig.types.uuid.BluetoothUUID


   .. py:attribute:: name
      :type:  str


.. py:class:: CharacteristicSpec

   Bases: :py:obj:`msgspec.Struct`


   Characteristic specification from cross-file YAML references.


   .. py:attribute:: uuid
      :type:  bluetooth_sig.types.uuid.BluetoothUUID


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: field_info
      :type:  FieldInfo


   .. py:attribute:: unit_info
      :type:  UnitMetadata


   .. py:attribute:: description
      :type:  str | None
      :value: None



   .. py:property:: data_type
      :type: str | None


      Get data type from field info.


   .. py:property:: field_size
      :type: str | None


      Get field size from field info.


   .. py:property:: unit_id
      :type: str | None


      Get unit ID from unit info.


   .. py:property:: unit_symbol
      :type: str | None


      Get unit symbol from unit info.


   .. py:property:: base_unit
      :type: str | None


      Get base unit from unit info.


   .. py:property:: resolution_text
      :type: str | None


      Get resolution text from unit info.


.. py:class:: FieldInfo

   Bases: :py:obj:`msgspec.Struct`


   Field-related metadata from YAML.


   .. py:attribute:: name
      :type:  str | None
      :value: None



   .. py:attribute:: data_type
      :type:  str | None
      :value: None



   .. py:attribute:: field_size
      :type:  str | None
      :value: None



   .. py:attribute:: description
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


   .. py:attribute:: value
      :type:  int


   .. py:property:: psm
      :type: int


      Alias for value when used as PSM.


.. py:class:: UnitMetadata

   Bases: :py:obj:`msgspec.Struct`


   Unit-related metadata from characteristic YAML specifications.

   This is embedded metadata within characteristic specs, distinct from
   the Units registry which uses UUID-based entries.


   .. py:attribute:: unit_id
      :type:  str | None
      :value: None



   .. py:attribute:: unit_symbol
      :type:  str | None
      :value: None



   .. py:attribute:: base_unit
      :type:  str | None
      :value: None



   .. py:attribute:: resolution_text
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


   .. py:attribute:: value
      :type:  int


   .. py:attribute:: name
      :type:  str


   .. py:property:: bit
      :type: int


      Alias for value when used as bit position.


.. py:class:: ValueNameReferenceInfo

   Bases: :py:obj:`msgspec.Struct`


   Generic info for registries with value, name, and reference fields.

   Used by: ad_types and similar registries with specification references.


   .. py:attribute:: value
      :type:  int


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: reference
      :type:  str


.. py:function:: generate_basic_aliases(info: BaseUuidInfo) -> set[str]

   Generate a small set of common alias keys for a BaseUuidInfo.

   Domain-specific heuristics remain the responsibility of the registry.


