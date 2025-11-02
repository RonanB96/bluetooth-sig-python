"""Async Bluetooth SIG standards translator."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from ..types import CharacteristicContext, CharacteristicData
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
        uuid: str,
        raw_data: bytes,
        ctx: CharacteristicContext | None = None,
        descriptor_data: dict[str, bytes] | None = None,
    ) -> CharacteristicData:
        """Parse characteristic data asynchronously.

        This is a non-blocking variant that yields control to the event loop
        during parsing, allowing other tasks to run concurrently.

        Args:
            uuid: The characteristic UUID
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
        # Yield to event loop before CPU-intensive parsing
        await asyncio.sleep(0)

        # Delegate to sync implementation
        return self.parse_characteristic(uuid, raw_data, ctx, descriptor_data)

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
        # For small batches, parse directly
        if len(char_data) <= 5:
            await asyncio.sleep(0)
            return self.parse_characteristics(char_data, descriptor_data, ctx)

        # For larger batches, parse in chunks to yield to event loop
        results: dict[str, CharacteristicData] = {}
        chunk_size = 10
        items = list(char_data.items())

        for i in range(0, len(items), chunk_size):
            chunk = dict(items[i : i + chunk_size])

            # Yield to event loop between chunks
            await asyncio.sleep(0)

            # Parse chunk
            chunk_results = self.parse_characteristics(
                chunk,
                {k: v for k, v in (descriptor_data or {}).items() if k in chunk},
                ctx,
            )
            results.update(chunk_results)

        return results

    async def get_sig_info_by_uuid_async(self, uuid: str) -> SIGInfo | None:
        """Get SIG info by UUID asynchronously.

        Args:
            uuid: UUID string

        Returns:
            SIGInfo if found, None otherwise
        """
        await asyncio.sleep(0)
        return self.get_sig_info_by_uuid(uuid)

    async def get_sig_info_by_name_async(self, name: str) -> SIGInfo | None:
        """Get SIG info by name asynchronously.

        Args:
            name: Characteristic or service name

        Returns:
            SIGInfo if found, None otherwise
        """
        await asyncio.sleep(0)
        return self.get_sig_info_by_name(name)


# Convenience instance
AsyncBluetoothSIG = AsyncBluetoothSIGTranslator()
