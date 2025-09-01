"""Core BLE GATT device functionality."""

from typing import Dict, Optional

from ble_gatt_device.interfaces.ble_device_interface import BLEDeviceInterface
from ble_gatt_device.interfaces.bleak_device import BleakBLEDevice


class BLEGATTDevice:
    """Backend-agnostic BLE GATT device abstraction."""

    def __init__(self, address: str, backend: str = "bleak"):
        self.address = address
        if backend == "bleak":
            self._impl: BLEDeviceInterface = BleakBLEDevice(address)
        else:
            raise NotImplementedError(f"BLE backend '{backend}' is not implemented.")

    def __str__(self) -> str:
        """Return string representation of the device."""
        return f"BLEGATTDevice(address={self.address})"

    async def connect(self) -> bool:
        """Connect to the BLE device using the selected backend."""
        return await self._impl.connect()

    async def disconnect(self) -> None:
        """Disconnect from the BLE device using the selected backend."""
        await self._impl.disconnect()

    async def get_rssi(self) -> Optional[int]:
        """Get the RSSI of the BLE device using the selected backend."""
        return await self._impl.get_rssi()

    async def read_characteristics(self) -> Dict:
        """Read all supported characteristics using the selected backend."""
        return await self._impl.read_characteristics()

    async def read_parsed_characteristics(self) -> Dict:
        """Read and parse all supported characteristics using the selected backend."""
        return await self._impl.read_parsed_characteristics()

    async def get_device_info(self) -> Dict:
        """Get device information and discovered services using the selected backend."""
        return await self._impl.get_device_info()
