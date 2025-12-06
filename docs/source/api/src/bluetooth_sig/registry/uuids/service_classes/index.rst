src.bluetooth_sig.registry.uuids.service_classes
================================================

.. py:module:: src.bluetooth_sig.registry.uuids.service_classes

.. autoapi-nested-parse::

   Service classes registry for Bluetooth SIG service class UUIDs.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.service_classes.service_classes_registry


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.registry.uuids.service_classes.ServiceClassesRegistry


Module Contents
---------------

.. py:class:: ServiceClassesRegistry

   Bases: :py:obj:`bluetooth_sig.registry.base.BaseUUIDRegistry`\ [\ :py:obj:`bluetooth_sig.types.registry.service_class.ServiceClassInfo`\ ]


   Registry for Bluetooth SIG service class definitions.

   Initialize the registry.


   .. py:method:: get_all_service_classes() -> list[bluetooth_sig.types.registry.service_class.ServiceClassInfo]

      Get all service classes in the registry.

      :returns: List of all ServiceClassInfo objects



   .. py:method:: get_service_class_info(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bluetooth_sig.types.registry.service_class.ServiceClassInfo | None

      Get service class information by UUID.

      :param uuid: The UUID to look up (string, int, or BluetoothUUID)

      :returns: ServiceClassInfo if found, None otherwise



   .. py:method:: get_service_class_info_by_id(service_class_id: str) -> bluetooth_sig.types.registry.service_class.ServiceClassInfo | None

      Get service class information by service class ID.

      :param service_class_id: The service class ID to look up

      :returns: ServiceClassInfo if found, None otherwise



   .. py:method:: get_service_class_info_by_name(name: str) -> bluetooth_sig.types.registry.service_class.ServiceClassInfo | None

      Get service class information by name (case insensitive).

      :param name: The service class name to look up

      :returns: ServiceClassInfo if found, None otherwise



   .. py:method:: is_service_class_uuid(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bool

      Check if a UUID corresponds to a known service class.

      :param uuid: The UUID to check

      :returns: True if the UUID is a known service class, False otherwise



.. py:data:: service_classes_registry
   :value: None


