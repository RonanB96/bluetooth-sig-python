src.bluetooth_sig.registry.uuids.mesh_profiles
==============================================

.. py:module:: src.bluetooth_sig.registry.uuids.mesh_profiles

.. autoapi-nested-parse::

   Mesh profiles registry for Bluetooth SIG mesh profile definitions.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.mesh_profiles.mesh_profiles_registry


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.mesh_profiles.MeshProfilesRegistry


Module Contents
---------------

.. py:class:: MeshProfilesRegistry

   Bases: :py:obj:`bluetooth_sig.registry.base.BaseUUIDRegistry`\ [\ :py:obj:`bluetooth_sig.types.registry.mesh_profile_uuids.MeshProfileInfo`\ ]


   Registry for Bluetooth SIG mesh profile definitions.

   Initialize the registry.


   .. py:method:: get_all_mesh_profiles() -> list[bluetooth_sig.types.registry.mesh_profile_uuids.MeshProfileInfo]

      Get all mesh profiles in the registry.

      :returns: List of all MeshProfileInfo objects



   .. py:method:: get_mesh_profile_info(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bluetooth_sig.types.registry.mesh_profile_uuids.MeshProfileInfo | None

      Get mesh profile information by UUID.

      :param uuid: The UUID to look up (string, int, or BluetoothUUID)

      :returns: MeshProfileInfo if found, None otherwise



   .. py:method:: get_mesh_profile_info_by_name(name: str) -> bluetooth_sig.types.registry.mesh_profile_uuids.MeshProfileInfo | None

      Get mesh profile information by name (case insensitive).

      :param name: The mesh profile name to look up

      :returns: MeshProfileInfo if found, None otherwise



   .. py:method:: is_mesh_profile_uuid(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bool

      Check if a UUID corresponds to a known mesh profile.

      :param uuid: The UUID to check

      :returns: True if the UUID is a known mesh profile, False otherwise



.. py:data:: mesh_profiles_registry
   :value: None


