#!/usr/bin/env python3
"""Tests for examples that can run without real devices."""

from __future__ import annotations

import builtins
import importlib
import sys
import time
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from examples.advertising_parsing import main
from examples.utils.data_parsing import parse_and_display_results
from examples.utils.library_detection import AVAILABLE_LIBRARIES, show_library_availability
from examples.utils.mock_data import mock_ble_data
from examples.utils.models import ReadResult


class TestUtilityFunctions:
    """Test utility functions from the utils package."""

    def test_mock_ble_data(self) -> None:
        """Test mock BLE data generation."""
        data = mock_ble_data()

        assert isinstance(data, dict)
        assert "2A19" in data  # Battery Level
        assert "2A00" in data  # Device Name
        assert "2A6E" in data  # Temperature
        assert "2A6F" in data  # Humidity
        assert "2A6D" in data  # Pressure
        assert "2A29" in data  # Manufacturer Name

        # Check data types
        for _uuid, raw_data in data.items():
            assert isinstance(raw_data, bytes)

    @pytest.mark.asyncio
    async def test_parse_and_display_results(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test parsing and display of BLE results."""
        test_data = {
            "2A19": ReadResult(raw_data=bytes([0x64]), read_time=time.time()),  # 100% battery
            "2A00": ReadResult(raw_data=b"Test Device", read_time=time.time()),  # Device name
        }

        result = await parse_and_display_results(test_data, "Test Device")

        assert isinstance(result, dict)
        captured = capsys.readouterr()
        assert "Test Device Results with SIG Parsing:" in captured.out
        assert "Battery Level: 100" in captured.out
        assert "Device Name: Test Device" in captured.out

    def test_show_library_availability(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test library availability display."""
        show_library_availability()

        captured = capsys.readouterr()
        assert "BLE Library Availability Check" in captured.out
        assert "Available BLE libraries:" in captured.out

    def test_available_libraries(self) -> None:
        """Test AVAILABLE_LIBRARIES constant."""
        assert isinstance(AVAILABLE_LIBRARIES, dict)
        # Should be a dictionary of library configurations


class TestAdvertisingParsing:
    """Test advertising_parsing.py example without real devices."""

    async def _run_main_with_args(
        self, data: str | None = None, mock: bool = False, extended_mock: bool = False
    ) -> dict[str, Any]:
        """Helper method to run main with mocked arguments."""
        # Create mock args object
        mock_args = MagicMock()
        mock_args.data = data
        mock_args.mock = mock
        mock_args.extended_mock = extended_mock

        # Mock the parser.parse_args() method
        with patch("examples.advertising_parsing.create_common_parser") as mock_parser_func:
            mock_parser = MagicMock()
            mock_parser.parse_args.return_value = mock_args
            if not any([data, mock, extended_mock]):
                mock_parser.print_help = MagicMock()
            mock_parser_func.return_value = mock_parser

            return await main()

    @pytest.mark.asyncio
    async def test_advertising_parsing_with_mock_data(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test advertising parsing with mock data."""
        await self._run_main_with_args(mock=True)

        captured = capsys.readouterr()
        assert "📝 USING MOCK LEGACY ADVERTISING DATA FOR DEMONSTRATION" in captured.out
        assert "Mock BLE Device Results with SIG Parsing:" in captured.out
        assert "Local Name: Test Device" in captured.out
        assert "Service UUIDs:" in captured.out
        assert "180F: Battery" in captured.out

    @pytest.mark.asyncio
    async def test_advertising_parsing_with_hex_data(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test advertising parsing with provided hex data."""
        test_hex = "020106030318180f0962543532"
        await self._run_main_with_args(data=test_hex)

        captured = capsys.readouterr()
        assert "Parsing provided advertising data:" in captured.out
        assert f"Raw data: {test_hex}" in captured.out
        assert "Provided Data Results with SIG Parsing:" in captured.out

    @pytest.mark.asyncio
    async def test_advertising_parsing_invalid_hex(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test advertising parsing with invalid hex data."""
        await self._run_main_with_args(data="invalid_hex")

        captured = capsys.readouterr()
        assert "Invalid hex data provided" in captured.out


class TestPureSigParsing:
    """Test pure_sig_parsing.py example."""

    def test_pure_sig_parsing_demo(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test the pure SIG parsing demonstration."""
        from examples.pure_sig_parsing import demonstrate_pure_sig_parsing

        demonstrate_pure_sig_parsing()
        captured = capsys.readouterr()

        assert "Pure Bluetooth SIG Standards Parsing Demo" in captured.out
        assert "Battery Level" in captured.out
        assert "Device Name" in captured.out
        assert "Temperature" in captured.out

    def test_pure_sig_parsing_batch_demo(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test the batch parsing demonstration."""
        from examples.pure_sig_parsing import demonstrate_batch_parsing

        demonstrate_batch_parsing()
        captured = capsys.readouterr()

        assert "Batch Parsing Multiple Characteristics" in captured.out


class TestMockDataConsistency:
    """Test that mock data is consistent and parseable."""

    @pytest.mark.asyncio
    async def test_mock_data_parsing_consistency(self) -> None:
        """Test that all mock data can be parsed successfully."""
        mock_data = mock_ble_data()

        # Format data for parsing
        current_time = time.time()
        formatted_data = {uuid: ReadResult(raw_data=data, read_time=current_time) for uuid, data in mock_data.items()}

        # Parse the data
        results: dict[str, Any] = await parse_and_display_results(formatted_data, "Mock Test")

        # Verify all UUIDs were processed
        assert isinstance(results, dict)
        assert len(results) > 0

    def test_mock_ble_data_consistency(self) -> None:
        """Test that mock_ble_data returns consistent results."""
        data1 = mock_ble_data()
        data2 = mock_ble_data()

        # Should return the same structure
        assert set(data1.keys()) == set(data2.keys())

        # Should return the same values
        for uuid, value in data1.items():
            assert value == data2[uuid]


@pytest.mark.parametrize(
    "hex_data,expected_length",
    [
        ("64", 1),  # Single byte
        ("640A", 2),  # Two bytes
        ("02:01:06", 3),  # With colons
        ("02 01 06", 3),  # With spaces
        ("020106030318180f", 8),  # Longer advertising packet
    ],
)
def test_hex_data_conversion(hex_data: str, expected_length: int) -> None:
    """Test hex data conversion in advertising parsing."""
    # Remove separators and convert
    clean_hex = hex_data.replace(" ", "").replace(":", "")
    raw_data = bytes.fromhex(clean_hex)

    assert len(raw_data) == expected_length


def test_examples_utils_safe_import(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure the examples.utils package is safe to import when optional.

    external back-ends are absent.

    This test simulates ImportError for optional back-end modules and then
    imports the `examples.utils` package; the import must succeed because
    `examples.utils` no longer re-exports heavy adapter modules at
    package import time.
    """
    real_import = builtins.__import__

    def _fake_import(
        name: str,
        globals_: dict[str, object] | None = None,
        locals_: dict[str, object] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> object:
        root = name.split(".")[0]
        # Simulate missing optional back-ends
        if root in ("bleak", "bleak_retry_connector", "simplepyble", "simpleble"):
            raise ImportError(f"Simulated missing optional backend: {root}")
        return real_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    # Ensure a fresh import for the package under test
    sys.modules.pop("examples.utils", None)

    mod = importlib.import_module("examples.utils")
    assert hasattr(mod, "parse_and_display_results")


def test_bleak_retry_integration_missing_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure bleak-retry integration module raises a clear ImportError when back-ends are missing."""
    real_import = builtins.__import__

    def _fake_import(
        name: str,
        globals_: dict[str, Any] | None = None,
        locals_: dict[str, Any] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> object:
        root = name.split(".")[0]
        if root in ("bleak", "bleak_retry_connector"):
            raise ModuleNotFoundError(f"Simulated missing optional backend: {root}")
        return real_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    sys.modules.pop("examples.connection_managers.bleak_retry", None)

    with pytest.raises(ModuleNotFoundError) as excinfo:
        importlib.import_module("examples.connection_managers.bleak_retry")

    assert "bleak" in str(excinfo.value)


def test_simpleble_integration_missing_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure simpleble integration module raises a clear ImportError when back-ends are missing."""
    real_import = builtins.__import__

    def _fake_import(
        name: str,
        globals_: dict[str, Any] | None = None,
        locals_: dict[str, Any] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> object:
        root = name.split(".")[0]
        if root == "simplepyble":
            raise ModuleNotFoundError(f"Simulated missing optional backend: {root}")
        return real_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    sys.modules.pop("examples.utils.simpleble_integration", None)

    with pytest.raises(ModuleNotFoundError) as excinfo:
        importlib.import_module("examples.connection_managers.simpleble")

    assert "simplepyble" in str(excinfo.value)


class TestCanonicalShapes:
    """Test that examples use canonical data shapes (CharacteristicData, ReadResult)."""

    @pytest.mark.asyncio
    async def test_robust_device_reading_success_canonical_shape(self) -> None:
        """Test that robust_device_reading returns canonical CharacteristicData dict on success."""
        # This would normally require a real device, but we're testing the shape
        # In a real scenario, this would connect to a device and return parsed data
        # For testing purposes, we verify the function signature and return type
        import inspect

        from examples.with_bleak_retry import robust_device_reading

        sig = inspect.signature(robust_device_reading)
        return_annotation = sig.return_annotation

        # Verify return type annotation is canonical
        assert str(return_annotation) == "dict[str, CharacteristicData]"

    @pytest.mark.asyncio
    async def test_robust_device_reading_parse_failure_handling(self) -> None:
        """Test that robust_device_reading handles parse failures gracefully."""
        # This test verifies that when parsing fails, the function doesn't crash
        # and returns an empty or partial results dict
        from unittest.mock import AsyncMock, MagicMock, patch

        with patch("examples.connection_managers.bleak_retry.BleakRetryConnectionManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_manager_cls.return_value = mock_manager

            with patch("examples.with_bleak_retry.Device") as mock_device_cls:
                mock_device = MagicMock()
                mock_device_cls.return_value = mock_device

                # Mock device methods
                mock_device.connect = AsyncMock()
                mock_device.disconnect = AsyncMock()
                mock_device.discover_services = AsyncMock(return_value={})
                mock_device.read = AsyncMock(side_effect=Exception("Parse failed"))

                from examples.with_bleak_retry import robust_device_reading

                # Should not raise exception, should handle parse failure gracefully
                result = await robust_device_reading("00:11:22:33:44:55", retries=1)

                # Should return dict even on failure
                assert isinstance(result, dict)
                # Should be empty since all reads failed
                assert len(result) == 0

    @pytest.mark.asyncio
    async def test_robust_device_reading_connection_error_handling(self) -> None:
        """Test that robust_device_reading handles connection errors gracefully."""
        from unittest.mock import AsyncMock, MagicMock, patch

        with patch("examples.connection_managers.bleak_retry.BleakRetryConnectionManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_manager_cls.return_value = mock_manager

            with patch("examples.with_bleak_retry.Device") as mock_device_cls:
                mock_device = MagicMock()
                mock_device_cls.return_value = mock_device

                # Mock connection failure
                mock_device.connect = AsyncMock(side_effect=ConnectionError("Connection failed"))

                from examples.with_bleak_retry import robust_device_reading

                # Should handle connection errors gracefully
                with pytest.raises(ConnectionError):  # Connection failure should propagate
                    await robust_device_reading("00:11:22:33:44:55", retries=1)

    @pytest.mark.asyncio
    async def test_robust_service_discovery_canonical_shape(self) -> None:
        """Test that robust_service_discovery returns canonical CharacteristicData dict."""
        from bluetooth_sig.types.data_types import CharacteristicData
        from examples.with_bleak_retry import robust_service_discovery

        # Currently returns empty dict, but should maintain canonical shape
        result = await robust_service_discovery("00:11:22:33:44:55")

        assert isinstance(result, dict)
        # All values should be CharacteristicData instances if present
        for value in result.values():
            assert isinstance(value, CharacteristicData)

    def test_canonical_shape_imports(self) -> None:
        """Test that canonical shape types are properly imported."""
        # Verify that CharacteristicData is imported and available
        from bluetooth_sig.types.data_types import CharacteristicData

        # Should be able to instantiate (basic smoke test)
        # Note: This tests import availability, not full functionality
        assert CharacteristicData is not None


if __name__ == "__main__":
    pytest.main([__file__])
