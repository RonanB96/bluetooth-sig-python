src.bluetooth_sig.registry.uuids.units
======================================

.. py:module:: src.bluetooth_sig.registry.uuids.units

.. autoapi-nested-parse::

   Units registry for Bluetooth SIG unit definitions.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.units.units_registry


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.units.UnitsRegistry


Module Contents
---------------

.. py:class:: UnitsRegistry

   Bases: :py:obj:`bluetooth_sig.registry.base.BaseUUIDRegistry`\ [\ :py:obj:`bluetooth_sig.types.registry.units.UnitInfo`\ ]


   Registry for Bluetooth SIG unit UUIDs.


   .. py:method:: get_unit_info(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bluetooth_sig.types.registry.units.UnitInfo | None

      Get unit information by UUID.

      :param uuid: 16-bit UUID as string (with or without 0x) or BluetoothUUID

      :returns: UnitInfo object, or None if not found



   .. py:method:: get_unit_info_by_name(name: str) -> bluetooth_sig.types.registry.units.UnitInfo | None

      Get unit information by name.

      :param name: Unit name (case-insensitive)

      :returns: UnitInfo object, or None if not found



   .. py:method:: get_unit_info_by_id(unit_id: str) -> bluetooth_sig.types.registry.units.UnitInfo | None

      Get unit information by ID.

      :param unit_id: Unit ID (e.g., "org.bluetooth.unit.celsius")

      :returns: UnitInfo object, or None if not found



   .. py:method:: is_unit_uuid(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bool

      Check if a UUID is a registered unit UUID.

      :param uuid: UUID to check

      :returns: True if the UUID is a unit UUID, False otherwise



   .. py:method:: get_all_units() -> list[bluetooth_sig.types.registry.units.UnitInfo]

      Get all registered units.

      :returns: List of all UnitInfo objects



.. py:data:: units_registry

