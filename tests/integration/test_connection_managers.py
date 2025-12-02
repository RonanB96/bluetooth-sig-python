#!/usr/bin/env python3
"""Tests for connection manager implementations.

These tests verify actual behaviour of connection managers.
No skips allowed - if imports fail, the test fails.
"""

from __future__ import annotations

import inspect
from unittest.mock import MagicMock, Mock, patch

import pytest

from examples.connection_managers.bleak_retry import BleakRetryConnectionManager
from examples.connection_managers.bleak_utils import bleak_services_to_batch
from examples.connection_managers.bluepy import BluePyConnectionManager
from examples.connection_managers.simpleble import SimplePyBLEConnectionManager, simpleble_services_to_batch


class TestBleakRetryConnectionManager:
    """Test BleakRetryConnectionManager actual behaviour."""

    @pytest.fixture
    def manager(self) -> BleakRetryConnectionManager:
        """Create a BleakRetryConnectionManager instance for testing."""
        with patch("examples.connection_managers.bleak_retry.BleakClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.is_connected = False
            mock_client_class.return_value = mock_client
            return BleakRetryConnectionManager("AA:BB:CC:DD:EE:FF")

    @pytest.mark.asyncio
    async def test_address_property(self, manager: BleakRetryConnectionManager) -> None:
        """Test that address property returns the correct value."""
        assert manager.address == "AA:BB:CC:DD:EE:FF"

    @pytest.mark.asyncio
    async def test_is_connected_initial_state(self, manager: BleakRetryConnectionManager) -> None:
        """Test that is_connected is False initially."""
        assert manager.is_connected is False

    @pytest.mark.asyncio
    async def test_max_attempts_retry_logic(self) -> None:
        """Test that BleakRetryConnectionManager respects max_attempts."""
        with patch("examples.connection_managers.bleak_retry.BleakClient") as mock_client_class:
            # Make connect always fail
            mock_client = MagicMock()
            mock_client.connect.side_effect = OSError("Connection failed")
            mock_client_class.return_value = mock_client

            manager = BleakRetryConnectionManager("AA:BB:CC:DD:EE:FF", max_attempts=3)

            # Should raise after 3 attempts
            with pytest.raises(OSError, match="Connection failed"):
                await manager.connect()

            # Verify it tried 3 times
            assert mock_client.connect.call_count == 3

    @pytest.mark.asyncio
    async def test_service_caching(self) -> None:
        """Test that managers cache service discovery results."""
        with patch("examples.connection_managers.bleak_retry.BleakClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.is_connected = True
            mock_client.services = []

            # Make async methods actually async
            async def mock_connect() -> None:
                pass

            async def mock_disconnect() -> None:
                pass

            mock_client.connect = mock_connect
            mock_client.disconnect = mock_disconnect
            mock_client_class.return_value = mock_client

            manager = BleakRetryConnectionManager("AA:BB:CC:DD:EE:FF")

            # First call
            services1 = await manager.get_services()

            # Second call should return cached result
            services2 = await manager.get_services()

            # Should be the same list instance (cached)
            assert services1 is services2

            # Reconnecting should clear cache
            await manager.connect()
            await manager.disconnect()

            # After disconnect, cache should be cleared
            assert manager._cached_services is None


class TestConnectionManagerConsistency:
    """Test that all connection managers behave consistently."""

    def test_consistent_method_signatures(self) -> None:
        """Test that all managers have consistent method signatures."""
        managers = [
            ("BleakRetry", BleakRetryConnectionManager),
            ("SimplePyBLE", SimplePyBLEConnectionManager),
            ("BluePy", BluePyConnectionManager),
        ]

        # Get method signatures from first manager
        _, first_manager = managers[0]
        first_methods = {}

        for method_name in [
            "connect",
            "disconnect",
            "read_gatt_char",
            "write_gatt_char",
            "get_services",
        ]:
            method = getattr(first_manager, method_name)
            first_methods[method_name] = inspect.signature(method)

        # Compare with other managers
        for name, manager_class in managers[1:]:
            for method_name, expected_sig in first_methods.items():
                method = getattr(manager_class, method_name)
                actual_sig = inspect.signature(method)

                # Compare parameter names (ignoring 'self')
                expected_params = [p for p in expected_sig.parameters.keys() if p != "self"]
                actual_params = [p for p in actual_sig.parameters.keys() if p != "self"]

                assert expected_params == actual_params, (
                    f"{name}.{method_name} has different parameters: {actual_params} vs {expected_params}"
                )

    def test_all_managers_handle_address(self) -> None:
        """Test that all managers properly store and return address."""
        test_address = "AA:BB:CC:DD:EE:FF"

        # Test BleakRetry
        with patch("examples.connection_managers.bleak_retry.BleakClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.is_connected = False
            mock_client_class.return_value = mock_client
            bleak_instance = BleakRetryConnectionManager(test_address)
            assert bleak_instance.address == test_address

        # Test SimplePyBLE
        simpleble_instance = SimplePyBLEConnectionManager(test_address, timeout=10.0)
        assert simpleble_instance.address == test_address

        # Test BluePy
        bluepy_instance = BluePyConnectionManager(test_address)
        assert bluepy_instance.address == test_address


class TestConnectionManagerHelpers:
    """Test helper functions for connection managers."""

    def test_bleak_services_to_batch(self) -> None:
        """Test bleak_services_to_batch converts services correctly."""
        # Create mock service structure
        mock_descriptor = Mock()
        mock_descriptor.uuid = "2902"
        mock_descriptor.value = b"\x01\x00"

        mock_char = Mock()
        mock_char.uuid = "2A19"
        mock_char.properties = ["read", "notify"]
        mock_char.descriptors = [mock_descriptor]
        mock_char.value = b"\x64"

        mock_service = Mock()
        mock_service.characteristics = [mock_char]

        # Convert to batch
        batch = bleak_services_to_batch([mock_service])

        assert len(batch.items) == 1
        assert batch.items[0].uuid == "2A19"
        assert batch.items[0].raw_data == b"\x64"
        assert "read" in batch.items[0].properties
        assert "2902" in batch.items[0].descriptors

    def test_simpleble_services_to_batch(self) -> None:
        """Test simpleble_services_to_batch converts services correctly."""
        from unittest.mock import Mock

        # Create mock service structure
        mock_descriptor = Mock()
        mock_descriptor.uuid = "2902"
        mock_descriptor.value = b"\x01\x00"

        mock_char = Mock()
        mock_char.uuid = "2A19"
        mock_char.properties = ["read", "notify"]
        mock_char.descriptors = [mock_descriptor]
        mock_char.value = b"\x64"

        mock_service = Mock()
        mock_service.characteristics = [mock_char]

        # Convert to batch
        batch = simpleble_services_to_batch([mock_service])

        assert len(batch.items) == 1
        assert batch.items[0].uuid == "2A19"
        assert batch.items[0].raw_data == b"\x64"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
