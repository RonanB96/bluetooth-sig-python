src.bluetooth_sig.stream
========================

.. py:module:: src.bluetooth_sig.stream

.. autoapi-nested-parse::

   Streaming utilities for Bluetooth SIG parsing workflows.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /reference/api/src/bluetooth_sig/stream/pairing/index


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.stream.DependencyPairingBuffer


Package Contents
----------------

.. py:class:: DependencyPairingBuffer(*, translator: src.bluetooth_sig.core.translator.BluetoothSIGTranslator, required_uuids: set[str], group_key: Callable[[str, src.bluetooth_sig.gatt.characteristics.base.CharacteristicData], collections.abc.Hashable], on_pair: Callable[[dict[str, src.bluetooth_sig.gatt.characteristics.base.CharacteristicData]], None])

   Buffer and pair dependent characteristic notifications.

   Buffers incoming notifications until all required UUIDs for a grouping key
   are present, then batch-parses and invokes the callback. Order-independent.

   :param translator: BluetoothSIGTranslator instance for parsing characteristics.
   :param required_uuids: Set of UUID strings that must be present to form a complete pair.
   :param group_key: Function that extracts a grouping key from each parsed notification.
                     Called as ``group_key(uuid, parsed_result)`` and must return a hashable value.
   :param on_pair: Callback invoked with complete parsed pairs as
                   ``on_pair(results: dict[str, CharacteristicData])``.

   .. note:: Does not manage BLE subscriptions. Callers handle connection and notification setup.


   .. py:method:: ingest(uuid: str, data: bytes) -> None

      Ingest a single characteristic notification.

      :param uuid: Characteristic UUID string (16-bit or 128-bit).
      :param data: Raw bytes from the characteristic notification.



