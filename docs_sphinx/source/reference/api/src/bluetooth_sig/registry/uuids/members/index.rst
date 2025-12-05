src.bluetooth_sig.registry.uuids.members
========================================

.. py:module:: src.bluetooth_sig.registry.uuids.members

.. autoapi-nested-parse::

   Members registry for Bluetooth SIG member UUIDs.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.members.members_registry


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.members.MembersRegistry


Module Contents
---------------

.. py:class:: MembersRegistry

   Bases: :py:obj:`bluetooth_sig.registry.base.BaseUUIDRegistry`\ [\ :py:obj:`bluetooth_sig.types.registry.member_uuids.MemberInfo`\ ]


   Registry for Bluetooth SIG member company UUIDs.


   .. py:method:: get_member_name(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> str | None

      Get member company name by UUID.

      :param uuid: 16-bit UUID as string (with or without 0x), int, or BluetoothUUID

      :returns: Member company name, or None if not found



   .. py:method:: is_member_uuid(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bool

      Check if a UUID is a registered member company UUID.

      :param uuid: UUID to check

      :returns: True if the UUID is a member UUID, False otherwise



   .. py:method:: get_all_members() -> list[bluetooth_sig.types.registry.member_uuids.MemberInfo]

      Get all registered member companies.

      :returns: List of all MemberInfo objects



   .. py:method:: get_member_info_by_name(name: str) -> bluetooth_sig.types.registry.member_uuids.MemberInfo | None

      Get member information by company name.

      :param name: Company name (case-insensitive)

      :returns: MemberInfo object, or None if not found



.. py:data:: members_registry
   :value: None


