"""BLE device interface for backend abstraction."""

from abc import ABC, abstractmethod
from typing import Optional


class BLEDeviceInterface(ABC):
    """Abstract BLE device interface for backend-agnostic BLE operations."""

    def __init__(self, address: str):
        self.address = address

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the BLE device."""
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the BLE device."""
        raise NotImplementedError

    @abstractmethod
    async def get_rssi(self) -> Optional[int]:
        """Get the RSSI (Received Signal Strength Indicator) of the connected device."""
        raise NotImplementedError

    @abstractmethod
    async def read_characteristics(self) -> dict:
        """Read all supported characteristics."""
        raise NotImplementedError

    @abstractmethod
    async def read_parsed_characteristics(self) -> dict:
        """Read and parse all supported characteristics."""
        raise NotImplementedError

    @abstractmethod
    async def get_device_info(self) -> dict:
        """Get device information and discovered services."""
        raise NotImplementedError
