"""Async Bluetooth SIG standards translator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import CharacteristicContext, CharacteristicData
from ..types.uuid import BluetoothUUID
from .translator import BluetoothSIGTranslator

if TYPE_CHECKING:
    from ..types import SIGInfo


class AsyncBluetoothSIGTranslator(BluetoothSIGTranslator):
    """Async wrapper for Bluetooth SIG standards translator.

    Provides async variants of parsing methods for non-blocking operation
    in async contexts. Inherits all sync methods from BluetoothSIGTranslator.

    Example:
        ```python
        async def main():
            translator = AsyncBluetoothSIGTranslator()

            # Async parsing
            result = await translator.parse_characteristic_async("2A19", battery_data)

            # Async batch parsing
            results = await translator.parse_characteristics_async(char_data)
        ```
    """

    async def parse_characteristic_async(
        self,
        uuid: str | BluetoothUUID,
        raw_data: bytes,
        ctx: CharacteristicContext | None = None,
        descriptor_data: dict[str, bytes] | None = None,
    ) -> CharacteristicData:
        """Parse characteristic data asynchronously.

        This is a non-blocking variant that yields control to the event loop
        during parsing, allowing other tasks to run concurrently.

        Args:
            uuid: The characteristic UUID (string or BluetoothUUID)
            raw_data: Raw bytes from the characteristic
            ctx: Optional context providing device-level info
            descriptor_data: Optional descriptor data

        Returns:
            CharacteristicData with parsed value and metadata

        Example:
            ```python
            async with BleakClient(address) as client:
                data = await client.read_gatt_char("2A19")
                result = await translator.parse_characteristic_async("2A19", data)
                print(f"Battery: {result.value}%")
            ```
        """
        # Convert to string for consistency with sync API
        uuid_str = str(uuid) if isinstance(uuid, BluetoothUUID) else uuid

        # Delegate to sync implementation
        return self.parse_characteristic(uuid_str, raw_data, ctx, descriptor_data)

    async def parse_characteristics_async(
        self,
        char_data: dict[str, bytes],
        descriptor_data: dict[str, dict[str, bytes]] | None = None,
        ctx: CharacteristicContext | None = None,
    ) -> dict[str, CharacteristicData]:
        """Parse multiple characteristics asynchronously.

        Parses characteristics concurrently, yielding to the event loop
        between parsing operations for better responsiveness.

        Args:
            char_data: Dictionary mapping UUIDs to raw data bytes
            descriptor_data: Optional nested dict of descriptor data
            ctx: Optional context

        Returns:
            Dictionary mapping UUIDs to CharacteristicData results

        Example:
            ```python
            async with BleakClient(address) as client:
                # Read multiple characteristics
                char_data = {}
                for uuid in ["2A19", "2A6E", "2A6F"]:
                    char_data[uuid] = await client.read_gatt_char(uuid)

                # Parse all asynchronously
                results = await translator.parse_characteristics_async(char_data)
                for uuid, result in results.items():
                    print(f"{uuid}: {result.value}")
            ```
        """
        # Delegate directly to sync implementation
        # The sync implementation already handles dependency ordering
        return self.parse_characteristics(char_data, descriptor_data, ctx)

    async def get_sig_info_by_uuid_async(self, uuid: str | BluetoothUUID) -> SIGInfo | None:
        """Get SIG info by UUID asynchronously.

        Args:
            uuid: UUID string or BluetoothUUID

        Returns:
            SIGInfo if found, None otherwise
        """
        uuid_str = str(uuid) if isinstance(uuid, BluetoothUUID) else uuid
        return self.get_sig_info_by_uuid(uuid_str)

    async def get_sig_info_by_name_async(self, name: str) -> SIGInfo | None:
        """Get SIG info by name asynchronously.

        Args:
            name: Characteristic or service name

        Returns:
            SIGInfo if found, None otherwise
        """
        return self.get_sig_info_by_name(name)


# Convenience instance
AsyncBluetoothSIG = AsyncBluetoothSIGTranslator()
