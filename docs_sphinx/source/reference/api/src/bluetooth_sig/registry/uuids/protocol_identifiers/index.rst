src.bluetooth_sig.registry.uuids.protocol_identifiers
=====================================================

.. py:module:: src.bluetooth_sig.registry.uuids.protocol_identifiers

.. autoapi-nested-parse::

   Protocol identifiers registry for Bluetooth SIG protocol definitions.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.protocol_identifiers.protocol_identifiers_registry


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.protocol_identifiers.ProtocolIdentifiersRegistry


Module Contents
---------------

.. py:class:: ProtocolIdentifiersRegistry

   Bases: :py:obj:`bluetooth_sig.registry.base.BaseUUIDRegistry`\ [\ :py:obj:`bluetooth_sig.types.registry.protocol_identifiers.ProtocolInfo`\ ]


   Registry for Bluetooth protocol identifiers.

   Provides lookup of protocol information by UUID or name.
   Supports Classic Bluetooth protocols (L2CAP, RFCOMM, BNEP, AVDTP, etc.)
   and BLE protocols.


   .. py:method:: get_protocol_info(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bluetooth_sig.types.registry.protocol_identifiers.ProtocolInfo | None

      Get protocol information by UUID or name.

      :param uuid: Protocol UUID (string, int, or BluetoothUUID) or protocol name

      :returns: ProtocolInfo if found, None otherwise

      .. admonition:: Examples

         >>> registry = ProtocolIdentifiersRegistry()
         >>> info = registry.get_protocol_info("0x0100")
         >>> if info:
         ...     print(info.name)  # "L2CAP"
         >>> info = registry.get_protocol_info("RFCOMM")
         >>> if info:
         ...     print(info.uuid.short_form)  # "0003"



   .. py:method:: get_protocol_info_by_name(name: str) -> bluetooth_sig.types.registry.protocol_identifiers.ProtocolInfo | None

      Get protocol information by name (case insensitive).

      :param name: The protocol name to look up (e.g., "L2CAP", "RFCOMM")

      :returns: ProtocolInfo if found, None otherwise



   .. py:method:: is_known_protocol(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bool

      Check if a UUID corresponds to a known protocol.

      :param uuid: The UUID to check

      :returns: True if the UUID is a known protocol, False otherwise



   .. py:method:: get_all_protocols() -> list[bluetooth_sig.types.registry.protocol_identifiers.ProtocolInfo]

      Get all registered protocol identifiers.

      :returns: List of all ProtocolInfo objects



.. py:data:: protocol_identifiers_registry
   :value: None


