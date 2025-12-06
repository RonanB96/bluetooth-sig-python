src.bluetooth_sig.device.connection
===================================

.. py:module:: src.bluetooth_sig.device.connection

.. autoapi-nested-parse::

   Connection manager protocol for BLE transport adapters.

   Defines an async abstract base class that adapter implementations (Bleak,
   SimplePyBLE, etc.) must inherit from so the `Device` class can operate
   independently of the underlying BLE library.

   Adapters must provide async implementations of all abstract methods below.
   For sync-only libraries an adapter can run sync calls in a thread and
   expose an async interface.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.device.connection.ConnectionManagerProtocol


Module Contents
---------------

.. py:class:: ConnectionManagerProtocol(address: str)

   Bases: :py:obj:`abc.ABC`


   Abstract base class describing the transport operations Device expects.

   All methods are async so adapters can integrate naturally with async
   libraries like Bleak. Synchronous libraries must be wrapped by adapters
   to provide async interfaces.

   Subclasses MUST implement all abstract methods and properties.

   Initialize the connection manager.

   :param address: The Bluetooth device address (MAC address)


   .. py:method:: connect() -> None
      :abstractmethod:

      :async:


      Open a connection to the device.



   .. py:method:: disconnect() -> None
      :abstractmethod:

      :async:


      Close the connection to the device.



   .. py:method:: get_services() -> list[bluetooth_sig.types.device_types.DeviceService]
      :abstractmethod:

      :async:


      Return a structure describing services/characteristics from the adapter.

      The concrete return type depends on the adapter; `Device` uses
      this only for enumeration in examples. Adapters should provide
      iterable objects with `.characteristics` elements that have
      `.uuid` and `.properties` attributes, or the adapter can return
      a mapping.



   .. py:method:: pair() -> None
      :abstractmethod:

      :async:


      Pair with the device.

      Raises an exception if pairing fails.

      .. note::

         On macOS, pairing is automatic when accessing authenticated characteristics.
         This method may not be needed on that platform.



   .. py:method:: read_gatt_char(char_uuid: bluetooth_sig.types.uuid.BluetoothUUID) -> bytes
      :abstractmethod:

      :async:


      Read the raw bytes of a characteristic identified by `char_uuid`.



   .. py:method:: read_gatt_descriptor(desc_uuid: bluetooth_sig.types.uuid.BluetoothUUID) -> bytes
      :abstractmethod:

      :async:


      Read the raw bytes of a descriptor identified by `desc_uuid`.

      :param desc_uuid: The UUID of the descriptor to read

      :returns: The raw descriptor data as bytes



   .. py:method:: read_rssi() -> int
      :abstractmethod:

      :async:


      Read the RSSI (signal strength) of the connection.

      :returns: RSSI value in dBm (typically negative, e.g., -60)



   .. py:method:: scan(timeout: float = 5.0) -> list[bluetooth_sig.types.device_types.ScannedDevice]
      :classmethod:

      :abstractmethod:

      :async:


      Scan for nearby BLE devices.

      This is a class method that doesn't require an instance. Not all backends
      support scanning - check the `supports_scanning` class attribute.

      :param timeout: Scan duration in seconds (default: 5.0)

      :returns: List of discovered devices

      :raises NotImplementedError: If this backend doesn't support scanning



   .. py:method:: set_disconnected_callback(callback: Callable[[], None]) -> None
      :abstractmethod:


      Set a callback to be invoked when the device disconnects.

      :param callback: Function to call when disconnection occurs



   .. py:method:: start_notify(char_uuid: bluetooth_sig.types.uuid.BluetoothUUID, callback: Callable[[str, bytes], None]) -> None
      :abstractmethod:

      :async:


      Start notifications for `char_uuid` and invoke `callback(uuid, data)` on updates.



   .. py:method:: stop_notify(char_uuid: bluetooth_sig.types.uuid.BluetoothUUID) -> None
      :abstractmethod:

      :async:


      Stop notifications for `char_uuid`.



   .. py:method:: unpair() -> None
      :abstractmethod:

      :async:


      Unpair from the device.

      Raises an exception if unpairing fails.




   .. py:method:: write_gatt_char(char_uuid: bluetooth_sig.types.uuid.BluetoothUUID, data: bytes, response: bool = True) -> None
      :abstractmethod:

      :async:


      Write raw bytes to a characteristic identified by `char_uuid`.

      :param char_uuid: The UUID of the characteristic to write to
      :param data: The raw bytes to write
      :param response: If True, use write-with-response (wait for acknowledgment).
                       If False, use write-without-response (faster but no confirmation).
                       Default is True for reliability.



   .. py:method:: write_gatt_descriptor(desc_uuid: bluetooth_sig.types.uuid.BluetoothUUID, data: bytes) -> None
      :abstractmethod:

      :async:


      Write raw bytes to a descriptor identified by `desc_uuid`.

      :param desc_uuid: The UUID of the descriptor to write to
      :param data: The raw bytes to write



   .. py:property:: address
      :type: str


      Get the device address.

      :returns: Bluetooth device address (MAC address)

      .. note:: Subclasses may override this to provide address from underlying library.


   .. py:property:: is_connected
      :type: bool

      :abstractmethod:


      Check if the connection is currently active.

      :returns: True if connected to the device, False otherwise


   .. py:property:: mtu_size
      :type: int

      :abstractmethod:


      Get the negotiated MTU size in bytes.

      :returns: The MTU size negotiated for this connection (typically 23-512 bytes)


   .. py:property:: name
      :type: str

      :abstractmethod:


      Get the name of the device.

      :returns: The name of the device as a string


   .. py:attribute:: supports_scanning
      :type:  ClassVar[bool]
      :value: False



