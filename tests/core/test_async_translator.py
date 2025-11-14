"""Tests for async translator."""

import asyncio

import pytest

from bluetooth_sig.core import BluetoothSIGTranslator


@pytest.mark.asyncio
class TestAsyncTranslator:
    """Test async translator functionality."""

    async def test_parse_characteristic_async(self) -> None:
        """Test async characteristic parsing."""
        translator = BluetoothSIGTranslator()
        data = bytes([85])

        result = await translator.parse_characteristic_async("2A19", data)

        assert result.parse_success
        assert result.value == 85

    async def test_parse_characteristics_async_small_batch(self) -> None:
        """Test async batch parsing with small batch."""
        translator = BluetoothSIGTranslator()

        char_data = {
            "2A19": bytes([85]),
            "2A6E": bytes([0x64, 0x09]),
        }

        results = await translator.parse_characteristics_async(char_data)

        assert len(results) == 2
        assert results["2A19"].value == 85

    async def test_parse_characteristics_async_large_batch(self) -> None:
        """Test async batch parsing with large batch (chunking)."""
        translator = BluetoothSIGTranslator()

        # Create 20 characteristics with different unknown UUIDs to test chunking
        # Use sequential unknown UUIDs in valid format
        char_data = {}
        for i in range(20):
            # Use unknown but valid UUID format
            uuid = f"FFFF{i:04X}-0000-1000-8000-00805F9B34FB"
            char_data[uuid] = bytes([i * 5 % 100])

        results = await translator.parse_characteristics_async(char_data)

        # Should get results for all (even if parse_success=False)
        assert len(results) == 20

    async def test_concurrent_parsing(self) -> None:
        """Test concurrent parsing operations."""
        translator = BluetoothSIGTranslator()

        # Parse multiple characteristics concurrently
        tasks = [translator.parse_characteristic_async("2A19", bytes([i % 100])) for i in range(10)]

        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        assert all(r.parse_success for r in results)

    async def test_async_with_sync_compatibility(self) -> None:
        """Test that async translator maintains sync API."""
        translator = BluetoothSIGTranslator()

        # Sync call should still work
        sync_result = translator.parse_characteristic("2A19", bytes([85]))

        # Async call should work
        async_result = await translator.parse_characteristic_async("2A19", bytes([85]))

        assert sync_result.value == async_result.value

    async def test_async_context_manager(self) -> None:
        """Test async parsing session context manager."""
        from bluetooth_sig.core.async_context import AsyncParsingSession

        translator = BluetoothSIGTranslator()
        async with AsyncParsingSession(translator) as session:
            result1 = await session.parse("2A19", bytes([85]))
            _ = await session.parse("2A6E", bytes([0x64, 0x09]))

            assert result1.value == 85
            assert len(session.results) == 2

    async def test_inherited_sync_methods(self) -> None:
        """Test that inherited sync methods work correctly."""
        translator = BluetoothSIGTranslator()

        # Test get_sig_info_by_uuid (inherited sync method)
        info = translator.get_sig_info_by_uuid("2A19")
        assert info is not None
        assert info.name == "Battery Level"

        # Test get_sig_info_by_name (inherited sync method)
        info2 = translator.get_sig_info_by_name("Battery Level")
        assert info2 is not None
        # UUID is returned in full format
        assert "2A19" in str(info2.uuid).upper()


@pytest.mark.asyncio
class TestAsyncIntegrationPatterns:
    """Test common async integration patterns."""

    async def test_with_async_generator(self) -> None:
        """Test parsing with async generator."""
        from collections.abc import AsyncGenerator

        translator = BluetoothSIGTranslator()

        async def characteristic_stream() -> AsyncGenerator[tuple[str, bytes], None]:
            """Simulate async characteristic stream."""
            for i in range(10):
                await asyncio.sleep(0.01)  # Simulate delay
                yield ("2A19", bytes([i * 10]))

        results = []
        async for uuid, data in characteristic_stream():
            result = await translator.parse_characteristic_async(uuid, data)
            results.append(result)

        assert len(results) == 10

    async def test_with_task_group_gather(self) -> None:
        """Test parsing with asyncio.gather."""
        from bluetooth_sig.gatt.characteristics.base import CharacteristicData

        translator = BluetoothSIGTranslator()

        async def parse_task(uuid: str, data: bytes) -> CharacteristicData:
            return await translator.parse_characteristic_async(uuid, data)

        # Use gather for concurrent parsing
        task1 = parse_task("2A19", bytes([85]))
        task2 = parse_task("2A6E", bytes([0x64, 0x09]))

        result1, result2 = await asyncio.gather(task1, task2)

        assert result1.value == 85
        assert result2.parse_success

    async def test_async_batch_with_descriptors(self) -> None:
        """Test async batch parsing with descriptors."""
        translator = BluetoothSIGTranslator()

        char_data = {
            "2A19": bytes([85]),
            "2A6E": bytes([0x64, 0x09]),
        }

        results = await translator.parse_characteristics_async(char_data)

        assert len(results) == 2
        assert results["2A19"].value == 85


@pytest.mark.asyncio
class TestAsyncErrorHandling:
    """Test error handling in async operations."""

    async def test_async_parse_unknown_characteristic(self) -> None:
        """Test async parsing of unknown characteristic."""
        translator = BluetoothSIGTranslator()

        # Parse unknown UUID
        result = await translator.parse_characteristic_async("FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF", b"\x64")

        assert result.parse_success is False
        assert result.name == "Unknown"

    async def test_sync_method_for_unknown_uuid(self) -> None:
        """Test inherited sync method for unknown UUID."""
        translator = BluetoothSIGTranslator()

        # Use inherited sync method
        info = translator.get_sig_info_by_uuid("FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF")

        assert info is None

    async def test_async_empty_batch(self) -> None:
        """Test async batch parsing with empty input."""
        translator = BluetoothSIGTranslator()

        results = await translator.parse_characteristics_async({})

        assert len(results) == 0
