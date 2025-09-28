#!/usr/bin/env python3
"""Tests for examples that can run without real devices."""

import time
from unittest.mock import patch

import pytest

# Import example modules and utilities via package
from examples.utils import (
    AVAILABLE_LIBRARIES,
    mock_ble_data,
    parse_and_display_results,
    short_uuid,
    show_library_availability,
)


class TestUtilityFunctions:
    """Test utility functions from the utils package."""

    def test_mock_ble_data(self):
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

    def test_short_uuid(self):
        """Test UUID shortening function."""
        # Test full UUID to short
        full_uuid = "00002a19-0000-1000-8000-00805f9b34fb"
        assert short_uuid(full_uuid) == "2A19"

        # Test already short UUID
        short = "2a19"
        assert short_uuid(short) == "2A19"

        # Test empty UUID
        assert short_uuid("") == ""

        # Test invalid UUID (function takes last 4 characters)
        assert short_uuid("invalid") == "ALID"

    @pytest.mark.asyncio
    async def test_parse_and_display_results(self, capsys):
        """Test parsing and display of BLE results."""
        test_data = {
            "2A19": (bytes([0x64]), time.time()),  # 100% battery
            "2A00": (b"Test Device", time.time()),  # Device name
        }

        result = await parse_and_display_results(test_data, "Test Device")

        assert isinstance(result, dict)
        captured = capsys.readouterr()
        assert "Test Device Results with SIG Parsing:" in captured.out
        assert "Battery Level: 100 %" in captured.out
        assert "Device Name: Test Device" in captured.out

    def test_show_library_availability(self, capsys):
        """Test library availability display."""
        show_library_availability()

        captured = capsys.readouterr()
        assert "BLE Library Availability Check" in captured.out
        assert "Available BLE libraries:" in captured.out

    def test_available_libraries(self):
        """Test AVAILABLE_LIBRARIES constant."""
        assert isinstance(AVAILABLE_LIBRARIES, dict)
        # Should be a dictionary of library configurations


class TestAdvertisingParsing:
    """Test advertising_parsing.py example without real devices."""

    @pytest.mark.asyncio
    async def test_advertising_parsing_with_mock_data(self, capsys):
        """Test advertising parsing with mock data."""
        from examples.advertising_parsing import main

        # Mock sys.argv to simulate no --data argument
        with patch("sys.argv", ["advertising_parsing.py"]):
            await main()

        captured = capsys.readouterr()
        assert "No data provided, using mock BLE data for demonstration:" in captured.out
        assert "Mock BLE Device Results with SIG Parsing:" in captured.out
        assert "Battery Level:" in captured.out
        assert "Device Name:" in captured.out

    @pytest.mark.asyncio
    async def test_advertising_parsing_with_hex_data(self, capsys):
        """Test advertising parsing with provided hex data."""
        from examples.advertising_parsing import main

        # Mock sys.argv to simulate --data argument
        test_hex = "020106030318180f0962543532"
        with patch("sys.argv", ["advertising_parsing.py", "--data", test_hex]):
            await main()

        captured = capsys.readouterr()
        assert "Parsing provided advertising data:" in captured.out
        assert f"Raw data: {test_hex}" in captured.out
        assert "Provided Data Results with SIG Parsing:" in captured.out

    @pytest.mark.asyncio
    async def test_advertising_parsing_invalid_hex(self, capsys):
        """Test advertising parsing with invalid hex data."""
        from examples.advertising_parsing import main

        # Mock sys.argv with invalid hex
        with patch("sys.argv", ["advertising_parsing.py", "--data", "invalid_hex"]):
            await main()

        captured = capsys.readouterr()
        assert "Invalid hex data provided" in captured.out


class TestPureSigParsing:
    """Test pure_sig_parsing.py example."""

    def test_pure_sig_parsing_demo(self, capsys):
        """Test the pure SIG parsing demonstration."""
        from examples.pure_sig_parsing import demonstrate_pure_sig_parsing

        demonstrate_pure_sig_parsing()
        captured = capsys.readouterr()

        assert "Pure Bluetooth SIG Standards Parsing Demo" in captured.out
        assert "Battery Level" in captured.out
        assert "Device Name" in captured.out
        assert "Temperature" in captured.out

    def test_pure_sig_parsing_batch_demo(self, capsys):
        """Test the batch parsing demonstration."""
        from examples.pure_sig_parsing import demonstrate_batch_parsing

        demonstrate_batch_parsing()
        captured = capsys.readouterr()

        assert "Batch Parsing Multiple Characteristics" in captured.out


class TestMockDataConsistency:
    """Test that mock data is consistent and parseable."""

    @pytest.mark.asyncio
    async def test_mock_data_parsing_consistency(self):
        """Test that all mock data can be parsed successfully."""
        mock_data = mock_ble_data()

        # Format data for parsing
        current_time = time.time()
        formatted_data = {uuid: (data, current_time) for uuid, data in mock_data.items()}

        # Parse the data
        results = await parse_and_display_results(formatted_data, "Mock Test")

        # Verify all UUIDs were processed
        assert isinstance(results, dict)
        assert len(results) > 0

    def test_mock_ble_data_consistency(self):
        """Test that mock_ble_data returns consistent results."""
        data1 = mock_ble_data()
        data2 = mock_ble_data()

        # Should return the same structure
        assert set(data1.keys()) == set(data2.keys())

        # Should return the same values
        for uuid in data1:
            assert data1[uuid] == data2[uuid]


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
def test_hex_data_conversion(hex_data, expected_length):
    """Test hex data conversion in advertising parsing."""
    # Remove separators and convert
    clean_hex = hex_data.replace(" ", "").replace(":", "")
    raw_data = bytes.fromhex(clean_hex)

    assert len(raw_data) == expected_length


if __name__ == "__main__":
    pytest.main([__file__])
