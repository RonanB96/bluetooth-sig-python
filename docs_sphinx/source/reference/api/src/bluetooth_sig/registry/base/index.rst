src.bluetooth_sig.registry.base
===============================

.. py:module:: src.bluetooth_sig.registry.base

.. autoapi-nested-parse::

   Base registry class for Bluetooth SIG registries with UUID support.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.registry.base.T
   src.bluetooth_sig.registry.base.E
   src.bluetooth_sig.registry.base.C
   src.bluetooth_sig.registry.base.U


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.registry.base.RegistryMixin
   src.bluetooth_sig.registry.base.BaseGenericRegistry
   src.bluetooth_sig.registry.base.BaseUUIDRegistry
   src.bluetooth_sig.registry.base.BaseUUIDClassRegistry


Module Contents
---------------

.. py:data:: T

.. py:data:: E

.. py:data:: C

.. py:class:: RegistryMixin

   Mixin providing common registry patterns for singleton, thread safety, and lazy loading.

   This mixin contains shared functionality used by both info-based and class-based registries.


.. py:class:: BaseGenericRegistry

   Bases: :py:obj:`RegistryMixin`, :py:obj:`abc.ABC`, :py:obj:`Generic`\ [\ :py:obj:`T`\ ]


   Base class for generic Bluetooth SIG registries with singleton pattern and thread safety.

   For registries that are not UUID-based.


   .. py:method:: get_instance() -> BaseGenericRegistry[T]
      :classmethod:


      Get the singleton instance of the registry.



.. py:data:: U

.. py:class:: BaseUUIDRegistry

   Bases: :py:obj:`RegistryMixin`, :py:obj:`abc.ABC`, :py:obj:`Generic`\ [\ :py:obj:`U`\ ]


   Base class for Bluetooth SIG registries with singleton pattern, thread safety, and UUID support.

   Provides canonical storage, alias indices, and extensible hooks for UUID-based registries.

   Subclasses should:
   1. Call super().__init__() in their __init__ (base class sets self._loaded = False)
   2. Implement _load() to perform actual data loading (must set self._loaded = True when done)
   3. Optionally override _load_yaml_path() to return the YAML file path relative to bluetooth_sig/
   4. Optionally override _generate_aliases(info) for domain-specific alias heuristics
   5. Optionally override _post_store(info) for enrichment (e.g., unit mappings)
   6. Call _ensure_loaded() before accessing data (provided by base class)


   .. py:method:: get_info(identifier: str | bluetooth_sig.types.uuid.BluetoothUUID) -> U | None

      Get info by UUID, name, ID, or alias.

      :param identifier: UUID string/int/BluetoothUUID, or name/ID/alias

      :returns: Info if found, None otherwise



   .. py:method:: register_runtime_entry(entry: object) -> None

      Register a runtime UUID entry, preserving original SIG info if overridden.

      :param entry: Custom entry with uuid, name, id, etc.



   .. py:method:: remove_runtime_override(normalized_uuid: str) -> None

      Remove runtime override, restoring original SIG info if available.

      :param normalized_uuid: Normalized UUID string



   .. py:method:: list_registered() -> list[str]

      List all registered normalized UUIDs.



   .. py:method:: list_aliases(uuid: bluetooth_sig.types.uuid.BluetoothUUID) -> list[str]

      List all aliases for a normalized UUID.



   .. py:method:: get_instance() -> BaseUUIDRegistry[U]
      :classmethod:


      Get the singleton instance of the registry.



.. py:class:: BaseUUIDClassRegistry

   Bases: :py:obj:`RegistryMixin`, :py:obj:`abc.ABC`, :py:obj:`Generic`\ [\ :py:obj:`E`\ , :py:obj:`C`\ ]


   Base class for UUID-based registries that store classes with enum-keyed access.

   This registry type is designed for GATT characteristics and services that need:
   1. UUID → Class mapping (e.g., "2A19" → BatteryLevelCharacteristic class)
   2. Enum → Class mapping (e.g., CharacteristicName.BATTERY_LEVEL → BatteryLevelCharacteristic class)
   3. Runtime class registration with override protection
   4. Thread-safe singleton pattern with lazy loading

   Unlike BaseUUIDRegistry which stores info objects (metadata), this stores actual classes
   that can be instantiated.

   Subclasses should:
   1. Call super().__init__() in their __init__
   2. Implement _load() to perform class discovery (must set self._loaded = True)
   3. Implement _build_enum_map() to create the enum → class mapping
   4. Implement _discover_sig_classes() to find built-in SIG classes
   5. Optionally override _allows_sig_override() for custom override rules


   .. py:method:: register_class(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID | int, cls: type[C], override: bool = False) -> None

      Register a custom class at runtime.

      :param uuid: The UUID for this class (string, BluetoothUUID, or int)
      :param cls: The class to register
      :param override: Whether to override existing registrations

      :raises TypeError: If cls is not the correct type
      :raises ValueError: If UUID conflicts with existing registration and override=False,
          or if attempting to override SIG class without permission



   .. py:method:: unregister_class(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID | int) -> None

      Unregister a custom class.

      :param uuid: The UUID to unregister (string, BluetoothUUID, or int)



   .. py:method:: get_class_by_uuid(uuid: str | bluetooth_sig.types.uuid.BluetoothUUID | int) -> type[C] | None

      Get the class for a given UUID.

      Checks custom classes first, then SIG classes.

      :param uuid: The UUID to look up (string, BluetoothUUID, or int)

      :returns: The class if found, None otherwise



   .. py:method:: get_class_by_enum(enum_member: E) -> type[C] | None

      Get the class for a given enum member.

      :param enum_member: The enum member to look up

      :returns: The class if found, None otherwise



   .. py:method:: list_custom_uuids() -> list[bluetooth_sig.types.uuid.BluetoothUUID]

      List all custom registered UUIDs.

      :returns: List of UUIDs with custom class registrations



   .. py:method:: clear_enum_map_cache() -> None

      Clear the cached enum → class mapping.

      Useful when classes are registered/unregistered at runtime.



   .. py:method:: get_instance() -> BaseUUIDClassRegistry[E, C]
      :classmethod:


      Get the singleton instance of the registry.



