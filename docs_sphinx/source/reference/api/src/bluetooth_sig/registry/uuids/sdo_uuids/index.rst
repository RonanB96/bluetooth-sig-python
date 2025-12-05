src.bluetooth_sig.registry.uuids.sdo_uuids
==========================================

.. py:module:: src.bluetooth_sig.registry.uuids.sdo_uuids

.. autoapi-nested-parse::

   SDO UUIDs registry for Bluetooth SIG Special Development Organization UUIDs.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.sdo_uuids.sdo_uuids_registry


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.sdo_uuids.SdoUuidsRegistry


Module Contents
---------------

.. py:class:: SdoUuidsRegistry

   Bases: :py:obj:`bluetooth_sig.registry.base.BaseUUIDRegistry`\ [\ :py:obj:`bluetooth_sig.types.registry.sdo_uuids.SdoUuidInfo`\ ]


   Registry for Bluetooth SIG Special Development Organization UUIDs.


   .. py:method:: get_sdo_info(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bluetooth_sig.types.registry.sdo_uuids.SdoUuidInfo | None

      Get SDO information by UUID.

      :param uuid: The UUID to look up (string, int, or BluetoothUUID)

      :returns: SdoInfo if found, None otherwise



   .. py:method:: get_sdo_info_by_name(name: str) -> bluetooth_sig.types.registry.sdo_uuids.SdoUuidInfo | None

      Get SDO information by name (case insensitive).

      :param name: The SDO name to look up

      :returns: SdoInfo if found, None otherwise



   .. py:method:: get_sdo_info_by_id(sdo_id: str) -> bluetooth_sig.types.registry.sdo_uuids.SdoUuidInfo | None

      Get SDO information by SDO ID.

      :param sdo_id: The SDO ID to look up

      :returns: SdoInfo if found, None otherwise



   .. py:method:: is_sdo_uuid(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bool

      Check if a UUID corresponds to a known SDO.

      :param uuid: The UUID to check

      :returns: True if the UUID is a known SDO, False otherwise



   .. py:method:: get_all_sdo_uuids() -> list[bluetooth_sig.types.registry.sdo_uuids.SdoUuidInfo]

      Get all SDO UUIDs in the registry.

      :returns: List of all SdoInfo objects



.. py:data:: sdo_uuids_registry
   :value: None


