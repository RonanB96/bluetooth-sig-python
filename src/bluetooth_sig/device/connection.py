"""Connection manager protocol for BLE transport adapters.

Defines an async protocol that adapter implementations (Bleak, SimplePyBLE,
etc.) should follow so the `Device` class can operate independently of the
underlying BLE library.

Adapters should provide async implementations of the methods below. For
sync-only libraries an adapter can run sync calls in a thread and expose an
async interface.
"""

from __future__ import annotations

from typing import Any, Callable, Protocol


class ConnectionManagerProtocol(Protocol):
    """Protocol describing the transport operations Device expects.

    All methods are async so adapters can integrate naturally with async
    libraries like Bleak. Synchronous libraries can be wrapped by adapters.
    """

    address: str

    async def connect(self) -> None:  # pragma: no cover - implemented by adapter
        """Open a connection to the device."""
        raise NotImplementedError()

    async def disconnect(self) -> None:  # pragma: no cover - implemented by adapter
        """Close the connection to the device."""
        raise NotImplementedError()

    async def read_gatt_char(self, char_uuid: str) -> bytes:  # pragma: no cover
        """Read the raw bytes of a characteristic identified by `char_uuid`."""
        raise NotImplementedError()

    async def write_gatt_char(
        self, char_uuid: str, data: bytes
    ) -> None:  # pragma: no cover
        """Write raw bytes to a characteristic identified by `char_uuid`."""
        raise NotImplementedError()

    async def get_services(self) -> Any:  # pragma: no cover
        """Return a structure describing services/characteristics from the adapter.

        The concrete return type depends on the adapter; `Device` uses this
        only for enumeration in examples. Adapters should provide iterable
        objects with `.characteristics` elements that have `.uuid` and
        `.properties` attributes, or the adapter can return a mapping.
        """
        raise NotImplementedError()

    async def start_notify(
        self, char_uuid: str, callback: Callable[[str, bytes], None]
    ) -> None:  # pragma: no cover
        """Start notifications for `char_uuid` and invoke `callback(uuid, data)` on updates."""
        raise NotImplementedError()

    async def stop_notify(self, char_uuid: str) -> None:  # pragma: no cover
        """Stop notifications for `char_uuid`."""
        raise NotImplementedError()


__all__ = ["ConnectionManagerProtocol"]
