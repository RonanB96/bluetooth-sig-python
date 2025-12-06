src.bluetooth_sig.registry.utils
================================

.. py:module:: src.bluetooth_sig.registry.utils

.. autoapi-nested-parse::

   Common utilities for registry modules.



Functions
---------

.. autoapisummary::

   src.bluetooth_sig.registry.utils.find_bluetooth_sig_path
   src.bluetooth_sig.registry.utils.load_yaml_uuids
   src.bluetooth_sig.registry.utils.normalize_uuid_string
   src.bluetooth_sig.registry.utils.parse_bluetooth_uuid


Module Contents
---------------

.. py:function:: find_bluetooth_sig_path() -> pathlib.Path | None

   Find the Bluetooth SIG assigned_numbers directory.

   :returns: Path to the uuids directory, or None if not found


.. py:function:: load_yaml_uuids(file_path: pathlib.Path) -> list[dict[str, Any]]

   Load UUID entries from a YAML file.

   :param file_path: Path to the YAML file

   :returns: List of UUID entry dictionaries


.. py:function:: normalize_uuid_string(uuid: str | int) -> str

   Normalize a UUID string or int to uppercase hex without 0x prefix.

   :param uuid: UUID as string (with or without 0x) or int

   :returns: Normalized UUID string


.. py:function:: parse_bluetooth_uuid(uuid: str | int | bluetooth_sig.types.uuid.BluetoothUUID) -> bluetooth_sig.types.uuid.BluetoothUUID

   Parse various UUID formats into a BluetoothUUID.

   :param uuid: UUID as string (with or without 0x), int, or BluetoothUUID

   :returns: BluetoothUUID instance

   :raises ValueError: If UUID format is invalid


