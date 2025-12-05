src.bluetooth_sig.gatt.descriptors.registry
===========================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.registry

.. autoapi-nested-parse::

   Descriptor registry and resolution.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.registry.DescriptorRegistry


Module Contents
---------------

.. py:class:: DescriptorRegistry

   Registry for descriptor classes.


   .. py:method:: register(descriptor_class: type[src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor]) -> None
      :classmethod:


      Register a descriptor class.



   .. py:method:: get_descriptor_class(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> type[src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor] | None
      :classmethod:


      Get descriptor class for UUID.

      :param uuid: The descriptor UUID

      :returns: Descriptor class if found, None otherwise

      :raises ValueError: If uuid format is invalid



   .. py:method:: create_descriptor(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID | int) -> src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor | None
      :classmethod:


      Create descriptor instance for UUID.

      :param uuid: The descriptor UUID

      :returns: Descriptor instance if found, None otherwise

      :raises ValueError: If uuid format is invalid



   .. py:method:: list_registered_descriptors() -> list[str]
      :classmethod:


      List all registered descriptor UUIDs.



