"""Async Bluetooth SIG standards translator."""

from __future__ import annotations

from ..types import CharacteristicContext, CharacteristicData
from ..types.uuid import BluetoothUUID
from .translator import BluetoothSIGTranslator


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
        """Parse characteristic data in an async-compatible manner.

        This is an async wrapper that allows characteristic parsing to be used
        in async contexts. The actual parsing is performed synchronously as it's
        a fast, CPU-bound operation that doesn't benefit from async I/O.

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
        """Parse multiple characteristics in an async-compatible manner.

        This is an async wrapper for batch characteristic parsing. The parsing
        is performed synchronously as it's a fast, CPU-bound operation. This method
        allows batch parsing to be used naturally in async workflows.

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


# Convenience instance
AsyncBluetoothSIG = AsyncBluetoothSIGTranslator()
