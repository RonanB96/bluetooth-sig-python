src.bluetooth_sig.registry.uuids.object_types
=============================================

.. py:module:: src.bluetooth_sig.registry.uuids.object_types

.. autoapi-nested-parse::

   Object types registry for Bluetooth SIG object type definitions.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.object_types.object_types_registry


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.object_types.ObjectTypesRegistry


Module Contents
---------------

.. py:class:: ObjectTypesRegistry

   Bases: :py:obj:`bluetooth_sig.registry.base.BaseUUIDRegistry`\ [\ :py:obj:`bluetooth_sig.types.registry.object_types.ObjectTypeInfo`\ ]


   Registry for Bluetooth SIG Object Transfer Service (OTS) object types.


   .. py:method:: get_object_type_info(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bluetooth_sig.types.registry.object_types.ObjectTypeInfo | None

      Get object type information by UUID.

      :param uuid: 16-bit UUID as string (with or without 0x) or BluetoothUUID

      :returns: ObjectTypeInfo object, or None if not found



   .. py:method:: get_object_type_info_by_name(name: str) -> bluetooth_sig.types.registry.object_types.ObjectTypeInfo | None

      Get object type information by name.

      :param name: Object type name (case-insensitive)

      :returns: ObjectTypeInfo object, or None if not found



   .. py:method:: get_object_type_info_by_id(object_type_id: str) -> bluetooth_sig.types.registry.object_types.ObjectTypeInfo | None

      Get object type information by ID.

      :param object_type_id: Object type ID (e.g., "org.bluetooth.object.track")

      :returns: ObjectTypeInfo object, or None if not found



   .. py:method:: is_object_type_uuid(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bool

      Check if a UUID is a registered object type UUID.

      :param uuid: UUID to check

      :returns: True if the UUID is an object type UUID, False otherwise



   .. py:method:: get_all_object_types() -> list[bluetooth_sig.types.registry.object_types.ObjectTypeInfo]

      Get all registered object types.

      :returns: List of all ObjectTypeInfo objects



.. py:data:: object_types_registry
   :value: None


