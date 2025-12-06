src.bluetooth_sig.gatt.characteristics.registry
===============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.registry

.. autoapi-nested-parse::

   Bluetooth SIG GATT characteristic registry.

   This module contains the characteristic registry implementation and
   class mappings. CharacteristicName enum is now centralized in
   types.gatt_enums to avoid circular imports.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.registry.CharacteristicRegistry


Functions
---------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.registry.get_characteristic_class_map


Module Contents
---------------

.. py:class:: CharacteristicRegistry

   Bases: :py:obj:`src.bluetooth_sig.registry.base.BaseUUIDClassRegistry`\ [\ :py:obj:`src.bluetooth_sig.types.gatt_enums.CharacteristicName`\ , :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`\ ]


   Encapsulates all GATT characteristic registry operations.

   Initialize the class registry.


   .. py:method:: clear_cache() -> None
      :classmethod:


      Clear the characteristic class map cache (for testing).



   .. py:method:: clear_custom_registrations() -> None
      :classmethod:


      Clear all custom characteristic registrations (for testing).



   .. py:method:: create_characteristic(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic | None
      :classmethod:


      Create a characteristic instance from a UUID.

      :param uuid: The characteristic UUID (string, BluetoothUUID, or int)

      :returns: Characteristic instance if found, None if UUID not registered

      :raises ValueError: If uuid format is invalid



   .. py:method:: get_all_characteristics() -> dict[src.bluetooth_sig.types.gatt_enums.CharacteristicName, type[src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic]]
      :classmethod:


      Get all registered characteristic classes.



   .. py:method:: get_characteristic_class(name: src.bluetooth_sig.types.gatt_enums.CharacteristicName) -> type[src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic] | None
      :classmethod:


      Get the characteristic class for a given CharacteristicName enum.

      Backward compatibility wrapper for get_class_by_enum().



   .. py:method:: get_characteristic_class_by_uuid(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> type[src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic] | None
      :classmethod:


      Get the characteristic class for a given UUID.

      Backward compatibility wrapper for get_class_by_uuid().



   .. py:method:: list_all_characteristic_enums() -> list[src.bluetooth_sig.types.gatt_enums.CharacteristicName]
      :staticmethod:


      List all supported characteristic names as enum values.



   .. py:method:: list_all_characteristic_names() -> list[str]
      :staticmethod:


      List all supported characteristic names as strings.



   .. py:method:: register_characteristic_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int, char_cls: type[src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic], override: bool = False) -> None
      :classmethod:


      Register a custom characteristic class at runtime.

      Backward compatibility wrapper for register_class().



   .. py:method:: unregister_characteristic_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> None
      :classmethod:


      Unregister a custom characteristic class.

      Backward compatibility wrapper for unregister_class().



.. py:function:: get_characteristic_class_map() -> dict[src.bluetooth_sig.types.gatt_enums.CharacteristicName, type[src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic]]

   Get the current characteristic class map.

   Backward compatibility function that returns the current registry state.

   :returns: Dictionary mapping CharacteristicName enum to characteristic classes


