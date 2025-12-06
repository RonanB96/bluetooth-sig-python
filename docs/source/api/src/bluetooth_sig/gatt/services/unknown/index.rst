src.bluetooth_sig.gatt.services.unknown
=======================================

.. py:module:: src.bluetooth_sig.gatt.services.unknown

.. autoapi-nested-parse::

   Unknown service implementation for unregistered service UUIDs.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.unknown.UnknownService


Module Contents
---------------

.. py:class:: UnknownService(uuid: src.bluetooth_sig.types.uuid.BluetoothUUID, name: str | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Generic service for unknown/unregistered service UUIDs.

   This class is used for services discovered at runtime that are not
   in the Bluetooth SIG specification or custom registry. It provides
   basic functionality while allowing characteristic processing.

   Initialize an unknown service with minimal info.

   :param uuid: The service UUID
   :param name: Optional custom name (defaults to "Unknown Service (UUID)")


