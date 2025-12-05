src.bluetooth_sig.registry.uuids.browse_groups
==============================================

.. py:module:: src.bluetooth_sig.registry.uuids.browse_groups

.. autoapi-nested-parse::

   Browse groups registry for Bluetooth SIG browse group definitions.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.browse_groups.browse_groups_registry


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.browse_groups.BrowseGroupsRegistry


Module Contents
---------------

.. py:class:: BrowseGroupsRegistry

   Bases: :py:obj:`bluetooth_sig.registry.base.BaseUUIDRegistry`\ [\ :py:obj:`bluetooth_sig.types.registry.browse_group_identifiers.BrowseGroupInfo`\ ]


   Registry for Bluetooth SIG browse group identifiers.


   .. py:method:: get_browse_group_info(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bluetooth_sig.types.registry.browse_group_identifiers.BrowseGroupInfo | None

      Get browse group information by UUID.

      :param uuid: The UUID to look up (string, int, or BluetoothUUID)

      :returns: BrowseGroupInfo if found, None otherwise



   .. py:method:: get_browse_group_info_by_name(name: str) -> bluetooth_sig.types.registry.browse_group_identifiers.BrowseGroupInfo | None

      Get browse group information by name (case insensitive).

      :param name: The browse group name to look up

      :returns: BrowseGroupInfo if found, None otherwise



   .. py:method:: get_browse_group_info_by_id(browse_group_id: str) -> bluetooth_sig.types.registry.browse_group_identifiers.BrowseGroupInfo | None

      Get browse group information by browse group ID.

      :param browse_group_id: The browse group ID to look up

      :returns: BrowseGroupInfo if found, None otherwise



   .. py:method:: is_browse_group_uuid(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bool

      Check if a UUID corresponds to a known browse group.

      :param uuid: The UUID to check

      :returns: True if the UUID is a known browse group, False otherwise



   .. py:method:: get_all_browse_groups() -> list[bluetooth_sig.types.registry.browse_group_identifiers.BrowseGroupInfo]

      Get all browse groups in the registry.

      :returns: List of all BrowseGroupInfo objects



.. py:data:: browse_groups_registry
   :value: None


