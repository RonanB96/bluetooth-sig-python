src.bluetooth_sig.gatt.uuid_registry
====================================

.. py:module:: src.bluetooth_sig.gatt.uuid_registry

.. autoapi-nested-parse::

   UUID registry loading from Bluetooth SIG YAML files.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.uuid_registry.uuid_registry


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.uuid_registry.UuidRegistry


Module Contents
---------------

.. py:class:: UuidRegistry

   Registry for Bluetooth SIG UUIDs with canonical storage + alias indices.

   This registry stores a number of internal caches and mappings which
   legitimately exceed the default pylint instance attribute limit. The
   complexity is intentional and centralised; an inline disable is used to
   avoid noisy global configuration changes.

   Initialize the UUID registry.


   .. py:method:: clear_custom_registrations() -> None

      Clear all custom registrations (for testing).



   .. py:method:: get_byte_order_hint() -> str
      :staticmethod:


      Get byte order hint for Bluetooth SIG specifications.

      :returns: "little" - Bluetooth SIG uses little-endian by convention



   .. py:method:: get_characteristic_info(identifier: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bluetooth_sig.types.CharacteristicInfo | None

      Get information about a characteristic by UUID, name, or ID.



   .. py:method:: get_descriptor_info(identifier: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bluetooth_sig.types.registry.descriptor_types.DescriptorInfo | None

      Get information about a descriptor by UUID, name, or ID.



   .. py:method:: get_service_info(key: str | bluetooth_sig.types.uuid.BluetoothUUID) -> bluetooth_sig.types.ServiceInfo | None

      Get information about a service by UUID, name, or ID.



   .. py:method:: get_signed_from_data_type(data_type: str | None) -> bool

      Determine if data type is signed from GSS data type.

      :param data_type: GSS data type string (e.g., "sint16", "float32", "uint8")

      :returns: True if the type represents signed values, False otherwise



   .. py:method:: register_characteristic(uuid: bluetooth_sig.types.uuid.BluetoothUUID, name: str, identifier: str | None = None, unit: str | None = None, value_type: bluetooth_sig.types.gatt_enums.ValueType | None = None, override: bool = False) -> None

      Register a custom characteristic at runtime.

      :param uuid: The Bluetooth UUID for the characteristic
      :param name: Human-readable name
      :param identifier: Optional identifier (auto-generated if not provided)
      :param unit: Optional unit of measurement
      :param value_type: Optional value type
      :param override: If True, allow overriding existing entries



   .. py:method:: register_service(uuid: bluetooth_sig.types.uuid.BluetoothUUID, name: str, identifier: str | None = None, override: bool = False) -> None

      Register a custom service at runtime.

      :param uuid: The Bluetooth UUID for the service
      :param name: Human-readable name
      :param identifier: Optional identifier (auto-generated if not provided)
      :param override: If True, allow overriding existing entries



   .. py:method:: resolve_characteristic_spec(characteristic_name: str) -> src.bluetooth_sig.types.registry.CharacteristicSpec | None

      Resolve characteristic specification with rich YAML metadata.

      This method provides detailed characteristic information including data types,
      field sizes, units, and descriptions by cross-referencing multiple YAML sources.

      :param characteristic_name: Name of the characteristic (e.g., "Temperature", "Battery Level")

      :returns: CharacteristicSpec with full metadata, or None if not found

      .. admonition:: Example

         spec = uuid_registry.resolve_characteristic_spec("Temperature")
         if spec:
             print(f"UUID: {spec.uuid}, Unit: {spec.unit_symbol}, Type: {spec.data_type}")



.. py:data:: uuid_registry

