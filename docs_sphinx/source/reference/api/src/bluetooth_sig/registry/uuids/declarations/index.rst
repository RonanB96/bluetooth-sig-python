src.bluetooth_sig.registry.uuids.declarations
=============================================

.. py:module:: src.bluetooth_sig.registry.uuids.declarations

.. autoapi-nested-parse::

   Declarations registry for Bluetooth SIG declaration UUIDs.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.declarations.declarations_registry


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.declarations.DeclarationsRegistry


Module Contents
---------------

.. py:class:: DeclarationsRegistry

   Bases: :py:obj:`bluetooth_sig.registry.base.BaseUUIDRegistry`\ [\ :py:obj:`bluetooth_sig.types.registry.declarations.DeclarationInfo`\ ]


   Registry for Bluetooth SIG GATT attribute declarations.


   .. py:method:: get_declaration_info(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bluetooth_sig.types.registry.declarations.DeclarationInfo | None

      Get declaration information by UUID.

      :param uuid: The UUID to look up (string, int, or BluetoothUUID)

      :returns: DeclarationInfo if found, None otherwise



   .. py:method:: get_declaration_info_by_name(name: str) -> bluetooth_sig.types.registry.declarations.DeclarationInfo | None

      Get declaration information by name (case insensitive).

      :param name: The declaration name to look up

      :returns: DeclarationInfo if found, None otherwise



   .. py:method:: get_declaration_info_by_id(declaration_id: str) -> bluetooth_sig.types.registry.declarations.DeclarationInfo | None

      Get declaration information by declaration ID.

      :param declaration_id: The declaration ID to look up

      :returns: DeclarationInfo if found, None otherwise



   .. py:method:: is_declaration_uuid(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bool

      Check if a UUID corresponds to a known declaration.

      :param uuid: The UUID to check

      :returns: True if the UUID is a known declaration, False otherwise



   .. py:method:: get_all_declarations() -> list[bluetooth_sig.types.registry.declarations.DeclarationInfo]

      Get all declarations in the registry.

      :returns: List of all DeclarationInfo objects



.. py:data:: declarations_registry
   :value: None


