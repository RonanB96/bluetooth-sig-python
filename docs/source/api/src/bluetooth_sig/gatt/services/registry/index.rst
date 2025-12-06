src.bluetooth_sig.gatt.services.registry
========================================

.. py:module:: src.bluetooth_sig.gatt.services.registry

.. autoapi-nested-parse::

   Bluetooth SIG GATT service registry.

   This module contains the service registry implementation, including the
   ServiceName enum, service class mappings, and the GattServiceRegistry
   class. This was moved from __init__.py to follow Python best practices
   of keeping __init__.py files lightweight.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.registry.GattServiceRegistry


Functions
---------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.registry.get_service_class_map


Module Contents
---------------

.. py:class:: GattServiceRegistry

   Bases: :py:obj:`src.bluetooth_sig.registry.base.BaseUUIDClassRegistry`\ [\ :py:obj:`src.bluetooth_sig.types.gatt_enums.ServiceName`\ , :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`\ ]


   Registry for all supported GATT services.

   Initialize the class registry.


   .. py:method:: clear_custom_registrations() -> None
      :classmethod:


      Clear all custom service registrations (for testing).



   .. py:method:: create_service(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int, characteristics: src.bluetooth_sig.types.gatt_services.ServiceDiscoveryData) -> src.bluetooth_sig.gatt.services.base.BaseGattService | None
      :classmethod:


      Create a service instance for the given UUID and characteristics.

      :param uuid: Service UUID
      :param characteristics: Dict mapping characteristic UUIDs to CharacteristicInfo

      :returns: Service instance if found, None otherwise

      :raises ValueError: If uuid format is invalid



   .. py:method:: get_all_services() -> list[type[src.bluetooth_sig.gatt.services.base.BaseGattService]]
      :classmethod:


      Get all registered service classes.

      :returns: List of all registered service classes



   .. py:method:: get_service_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> type[src.bluetooth_sig.gatt.services.base.BaseGattService] | None
      :classmethod:


      Get the service class for a given UUID.

      :param uuid: The service UUID

      :returns: Service class if found, None otherwise

      :raises ValueError: If uuid format is invalid



   .. py:method:: get_service_class_by_name(name: str | src.bluetooth_sig.types.gatt_enums.ServiceName) -> type[src.bluetooth_sig.gatt.services.base.BaseGattService] | None
      :classmethod:


      Get the service class for a given name or enum.



   .. py:method:: get_service_class_by_uuid(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> type[src.bluetooth_sig.gatt.services.base.BaseGattService] | None
      :classmethod:


      Get the service class for a given UUID (alias for get_service_class).



   .. py:method:: register_service_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int, service_cls: type[src.bluetooth_sig.gatt.services.base.BaseGattService], override: bool = False) -> None
      :classmethod:


      Register a custom service class at runtime.

      :param uuid: The service UUID
      :param service_cls: The service class to register
      :param override: Whether to override existing registrations

      :raises TypeError: If service_cls does not inherit from BaseGattService
      :raises ValueError: If UUID conflicts with existing registration and override=False



   .. py:method:: supported_service_names() -> list[str]
      :classmethod:


      Get a list of supported service names.



   .. py:method:: supported_services() -> list[str]
      :classmethod:


      Get a list of supported service UUIDs.



   .. py:method:: unregister_service_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> None
      :classmethod:


      Unregister a custom service class.

      :param uuid: The service UUID to unregister



.. py:function:: get_service_class_map() -> dict[src.bluetooth_sig.types.gatt_enums.ServiceName, type[src.bluetooth_sig.gatt.services.base.BaseGattService]]

   Get the current service class map.

   :returns: Dictionary mapping ServiceName enum to service classes


