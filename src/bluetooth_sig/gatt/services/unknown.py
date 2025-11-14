"""Unknown service implementation for unregistered service UUIDs."""

from ...types import ServiceInfo
from ...types.uuid import BluetoothUUID
from .base import BaseGattService


class UnknownService(BaseGattService):
    """Generic service for unknown/unregistered service UUIDs.

    This class is used for services discovered at runtime that are not
    in the Bluetooth SIG specification or custom registry. It provides
    basic functionality while allowing characteristic processing.
    """

    # TODO
    _is_base_class = True  # Exclude from registry validation tests (requires uuid parameter)

    def __init__(self, uuid: BluetoothUUID, name: str | None = None) -> None:
        """Initialize an unknown service with minimal info.

        Args:
            uuid: The service UUID
            name: Optional custom name (defaults to "Unknown Service (UUID)")

        """
        info = ServiceInfo(
            uuid=uuid,
            name=name or f"Unknown Service ({uuid})",
            description="",
        )
        super().__init__(info=info)
